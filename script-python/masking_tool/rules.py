"""Masking rule loading and validation."""
import csv
import re
from dataclasses import dataclass, field

NAME_DATA_TYPES = {
    "people_firstname",
    "people_firstname_kana",
    "people_lastname",
    "people_lastname_kana",
    "people_fullname",
    "people_fullname_kana",
}
DATA_TYPES = NAME_DATA_TYPES | {"email", "tel", "date"}

TEL_RULES = {"replace_all", "replace_last_4"}
DATE_RULE_RE = re.compile(r"^(year|month|day)_(\d+)$")
PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")
EMAIL_PLACEHOLDERS = {
    "firstname", "lastname", "fullname",
    "firstname_kana", "lastname_kana", "fullname_kana",
    "firstname_romaji", "lastname_romaji", "fullname_romaji",
    "row_id",
}
REQUIRED_HEADER = ["table_name", "column_name", "data_type", "data_rule"]


class RuleError(Exception):
    pass


@dataclass
class Rule:
    table_name: str
    column_name: str
    data_type: str
    data_rule: str
    line_no: int = 0


@dataclass
class TableRules:
    table: str
    locale: str
    rules: list = field(default_factory=list)


def load_rules(path, known_locales):
    """Load and validate rules; return an ordered {table_name: TableRules}."""
    rules = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None or [h.strip() for h in header[:4]] != REQUIRED_HEADER:
            raise RuleError(
                f"{path}: header must start with {','.join(REQUIRED_HEADER)}"
            )
        for line_no, row in enumerate(reader, start=2):
            if not row or not row[0].strip() or row[0].lstrip().startswith("#"):
                continue
            if len(row) < 4:
                raise RuleError(f"{path} line {line_no}: expected 4 columns")
            rules.append(Rule(
                table_name=row[0].strip(),
                column_name=row[1].strip(),
                data_type=row[2].strip(),
                data_rule=row[3].strip(),
                line_no=line_no,
            ))
    if not rules:
        raise RuleError(f"{path}: no rules found")
    _validate(path, rules, known_locales)
    return _group_by_table(path, rules, known_locales)


def _validate(path, rules, known_locales):
    seen = set()
    for rule in rules:
        where = f"{path} line {rule.line_no}"
        if rule.data_type not in DATA_TYPES:
            raise RuleError(f"{where}: unknown data_type '{rule.data_type}'")
        key = (rule.table_name, rule.column_name)
        if key in seen:
            raise RuleError(f"{where}: duplicate rule for {rule.table_name}.{rule.column_name}")
        seen.add(key)
        if rule.data_type in NAME_DATA_TYPES:
            if rule.data_rule not in known_locales:
                raise RuleError(
                    f"{where}: unknown locale '{rule.data_rule}' "
                    f"(available: {', '.join(sorted(known_locales))})"
                )
        elif rule.data_type == "tel":
            if rule.data_rule not in TEL_RULES:
                raise RuleError(
                    f"{where}: tel data_rule must be one of {', '.join(sorted(TEL_RULES))}"
                )
        elif rule.data_type == "date":
            if not DATE_RULE_RE.match(rule.data_rule):
                raise RuleError(
                    f"{where}: date data_rule must be year_<n>, month_<n> or day_<n>"
                )
        elif rule.data_type == "email":
            if not rule.data_rule:
                raise RuleError(f"{where}: email data_rule (pattern) must not be empty")
            for placeholder in PLACEHOLDER_RE.findall(rule.data_rule):
                if placeholder not in EMAIL_PLACEHOLDERS:
                    raise RuleError(
                        f"{where}: unknown placeholder '{{{placeholder}}}' "
                        f"(available: {', '.join(sorted(EMAIL_PLACEHOLDERS))})"
                    )


def _group_by_table(path, rules, known_locales):
    tables = {}
    for rule in rules:
        table_rules = tables.setdefault(
            rule.table_name, TableRules(table=rule.table_name, locale="")
        )
        table_rules.rules.append(rule)
        if rule.data_type in NAME_DATA_TYPES:
            if not table_rules.locale:
                table_rules.locale = rule.data_rule
            elif table_rules.locale != rule.data_rule:
                raise RuleError(
                    f"{path} line {rule.line_no}: table '{rule.table_name}' mixes "
                    f"locales '{table_rules.locale}' and '{rule.data_rule}' — all name "
                    f"rules of one table must use the same locale"
                )
    return tables
