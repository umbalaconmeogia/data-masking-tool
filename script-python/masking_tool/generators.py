"""Value generation per data_type."""
import calendar
import datetime
import re

from .rules import DATE_RULE_RE, PLACEHOLDER_RE

FULLWIDTH_DIGITS = "０１２３４５６７８９"

NAME_FIELDS = {
    "people_firstname": "firstname",
    "people_firstname_kana": "firstname_kana",
    "people_lastname": "lastname",
    "people_lastname_kana": "lastname_kana",
    "people_fullname": "fullname",
    "people_fullname_kana": "fullname_kana",
}

DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(.*)$")


def generate_value(rule, persona, row_id, original_value, rng):
    """Return the masked value for one cell (may return original for NULLs)."""
    if rule.data_type in NAME_FIELDS:
        return getattr(persona, NAME_FIELDS[rule.data_type])
    if rule.data_type == "email":
        return render_pattern(rule.data_rule, persona.as_dict(row_id))
    if rule.data_type == "tel":
        return mask_tel(original_value, rule.data_rule, rng)
    if rule.data_type == "date":
        return mask_date(original_value, rule.data_rule, rng)
    raise ValueError(f"unsupported data_type '{rule.data_type}'")


def render_pattern(pattern, values):
    return PLACEHOLDER_RE.sub(lambda m: values[m.group(1)], pattern)


def mask_tel(original, mode, rng):
    """Replace digits with random digits, keeping every non-digit character.

    replace_last_4 only touches the last 4 digit positions. NULL/empty
    values are returned unchanged.
    """
    if original is None or original == "":
        return original
    text = str(original)
    digit_positions = [
        i for i, ch in enumerate(text) if ch.isascii() and ch.isdigit() or ch in FULLWIDTH_DIGITS
    ]
    if not digit_positions:
        return original
    if mode == "replace_last_4":
        digit_positions = digit_positions[-4:]
    chars = list(text)
    for i in digit_positions:
        digit = rng.randrange(10)
        chars[i] = FULLWIDTH_DIGITS[digit] if chars[i] in FULLWIDTH_DIGITS else str(digit)
    return "".join(chars)


def _shift_date(value, unit, amount):
    if unit == "day":
        return value + datetime.timedelta(days=amount)
    months = amount if unit == "month" else amount * 12
    total = value.year * 12 + (value.month - 1) + months
    year, month = divmod(total, 12)
    month += 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def mask_date(original, rule, rng):
    """Shift a date by a random non-zero offset within ±n of the rule's unit.

    Accepts datetime.date/datetime values or 'YYYY-MM-DD[...]' strings;
    the original representation (and any time part) is preserved.
    NULL/empty values are returned unchanged.
    """
    if original is None or original == "":
        return original
    match = DATE_RULE_RE.match(rule)
    unit, n = match.group(1), int(match.group(2))
    if n == 0:
        return original
    amount = rng.choice([i for i in range(-n, n + 1) if i != 0])

    if isinstance(original, datetime.datetime) or isinstance(original, datetime.date):
        return _shift_date(original, unit, amount)

    text = str(original)
    date_match = DATE_RE.match(text)
    if not date_match:
        return original  # unrecognized format: leave untouched rather than corrupt
    year, month, day, rest = date_match.groups()
    shifted = _shift_date(datetime.date(int(year), int(month), int(day)), unit, amount)
    return f"{shifted.year:04d}-{shifted.month:02d}-{shifted.day:02d}{rest}"
