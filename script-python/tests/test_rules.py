import pytest

from masking_tool.rules import RuleError, load_rules

LOCALES = {"japanese", "vietnamese"}


def write_rules(tmp_path, body):
    path = tmp_path / "rules.csv"
    path.write_text("table_name,column_name,data_type,data_rule\n" + body, encoding="utf-8")
    return str(path)


def test_valid_rules_grouped(tmp_path):
    path = write_rules(tmp_path, "\n".join([
        "employees,name,people_fullname,japanese",
        "employees,tel,tel,replace_all",
        "# comment line",
        "companies,fax,tel,replace_last_4",
        "members,email,email,{firstname_romaji}.{row_id}@example.com",
    ]))
    tables = load_rules(path, LOCALES)
    assert set(tables) == {"employees", "companies", "members"}
    assert tables["employees"].locale == "japanese"
    assert tables["companies"].locale == ""  # falls back to default at runtime
    assert len(tables["employees"].rules) == 2


def test_bad_header(tmp_path):
    path = tmp_path / "rules.csv"
    path.write_text("table,col,type,rule\nemployees,name,people_fullname,japanese\n")
    with pytest.raises(RuleError, match="header"):
        load_rules(str(path), LOCALES)


def test_unknown_data_type(tmp_path):
    path = write_rules(tmp_path, "employees,name,people_nickname,japanese\n")
    with pytest.raises(RuleError, match="unknown data_type"):
        load_rules(path, LOCALES)


def test_unknown_locale(tmp_path):
    path = write_rules(tmp_path, "employees,name,people_fullname,german\n")
    with pytest.raises(RuleError, match="unknown locale"):
        load_rules(path, LOCALES)


def test_bad_tel_rule(tmp_path):
    path = write_rules(tmp_path, "employees,tel,tel,replace_first_4\n")
    with pytest.raises(RuleError, match="tel data_rule"):
        load_rules(path, LOCALES)


def test_bad_date_rule(tmp_path):
    path = write_rules(tmp_path, "employees,birthday,date,week_2\n")
    with pytest.raises(RuleError, match="date data_rule"):
        load_rules(path, LOCALES)


def test_unknown_email_placeholder(tmp_path):
    path = write_rules(tmp_path, "employees,email,email,{nickname}@example.com\n")
    with pytest.raises(RuleError, match="unknown placeholder"):
        load_rules(path, LOCALES)


def test_mixed_locales_rejected(tmp_path):
    path = write_rules(tmp_path, "\n".join([
        "employees,name,people_fullname,japanese",
        "employees,name2,people_fullname,vietnamese",
    ]))
    with pytest.raises(RuleError, match="mixes"):
        load_rules(path, LOCALES)


def test_duplicate_column_rejected(tmp_path):
    path = write_rules(tmp_path, "\n".join([
        "employees,tel,tel,replace_all",
        "employees,tel,tel,replace_last_4",
    ]))
    with pytest.raises(RuleError, match="duplicate"):
        load_rules(path, LOCALES)
