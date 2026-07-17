"""End-to-end test: mask a sqlite DB built from the companies/employees fixture."""
import csv
import os
import sqlite3

import pytest

from masking_tool.cli import main

HERE = os.path.dirname(__file__)
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SCHEMA_SQL = os.path.join(HERE, "fixtures", "schema-sqlite.sql")
TEST_DATA_DIR = os.path.join(ROOT, "docker", "test-data")
RULE_FILE = os.path.join(ROOT, "masking-rule.example.csv")


@pytest.fixture
def demo_db(tmp_path):
    """Build a sqlite DB from the schema + the shared docker/test-data CSVs."""
    db_path = str(tmp_path / "demo.sqlite")
    con = sqlite3.connect(db_path)
    with open(SCHEMA_SQL, encoding="utf-8") as f:
        con.executescript(f.read())
    for table in ("companies", "employees"):
        with open(os.path.join(TEST_DATA_DIR, f"{table}.csv"),
                  encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            columns = next(reader)
            placeholders = ", ".join("?" * len(columns))
            con.executemany(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                list(reader),
            )
    con.commit()
    con.close()
    return db_path


@pytest.fixture
def env_file(tmp_path, demo_db):
    path = tmp_path / ".env"
    path.write_text(f"DB_DRIVER=sqlite\nDB_NAME={demo_db}\nMASK_SEED=42\n")
    return str(path)


def fetch_all(db_path, query):
    con = sqlite3.connect(db_path)
    rows = con.execute(query).fetchall()
    con.close()
    return rows


EMPLOYEE_QUERY = (
    "SELECT id, name, name_kana, birthday, email, tel, fax, address, postal_code "
    "FROM employees ORDER BY id"
)


def run_cli(env_file, extra_args=()):
    return main(["--env", env_file, "--rule", RULE_FILE, *extra_args])


def test_masking_end_to_end(env_file, demo_db, tmp_path):
    before = fetch_all(demo_db, EMPLOYEE_QUERY)
    backup_path = str(tmp_path / "backup.csv")
    assert run_cli(env_file, ["--backup", backup_path]) == 0
    after = fetch_all(demo_db, EMPLOYEE_QUERY)

    assert len(after) == len(before) == 100
    for (id0, name0, kana0, bday0, email0, tel0, fax0, addr0, zip0), \
            (id1, name1, kana1, bday1, email1, tel1, fax1, addr1, zip1) in zip(before, after):
        assert id0 == id1
        # Masked columns changed
        assert name1 != name0
        assert kana1 != kana0
        assert email1 != email0
        # Row consistency: fullname parts pair with kana, email derives from romaji
        assert "　" in name1 and "　" in kana1
        local_part, _, domain = email1.partition("@")
        assert domain == "example.com"
        assert local_part.endswith(f".{id1}")
        # Birthday shifted within ±3 years, month/day preserved
        assert bday1 != bday0
        assert abs(int(bday1[:4]) - int(bday0[:4])) <= 3
        assert bday1[4:] == bday0[4:]
        # Tel: replace_all keeps shape; fax: replace_last_4 keeps prefix
        assert len(tel1) == len(tel0)
        assert [i for i, c in enumerate(tel1) if not c.isdigit()] == \
               [i for i, c in enumerate(tel0) if not c.isdigit()]
        assert fax1[:-4] == fax0[:-4]
        # Unmasked columns untouched
        assert addr1 == addr0
        assert zip1 == zip0

    # Backup mapping matches actual before/after values
    before_map = {row[0]: row for row in before}
    after_map = {row[0]: row for row in after}
    col_index = {"name": 1, "name_kana": 2, "birthday": 3, "email": 4, "tel": 5, "fax": 6}
    with open(backup_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "table_name", "column_name", "pk_value", "original_value", "new_value"
        ]
        backup_rows = [r for r in reader if r["table_name"] == "employees"]
    assert backup_rows
    for row in backup_rows:
        pk = int(row["pk_value"])
        idx = col_index[row["column_name"]]
        assert str(before_map[pk][idx]) == row["original_value"]
        assert str(after_map[pk][idx]) == row["new_value"]


def test_dry_run_changes_nothing(env_file, demo_db):
    before = fetch_all(demo_db, EMPLOYEE_QUERY)
    assert run_cli(env_file, ["--dry-run"]) == 0
    assert fetch_all(demo_db, EMPLOYEE_QUERY) == before


def test_tables_filter(env_file, demo_db):
    companies_before = fetch_all(demo_db, "SELECT * FROM companies ORDER BY id")
    employees_before = fetch_all(demo_db, EMPLOYEE_QUERY)
    assert run_cli(env_file, ["--tables", "companies"]) == 0
    assert fetch_all(demo_db, EMPLOYEE_QUERY) == employees_before
    assert fetch_all(demo_db, "SELECT * FROM companies ORDER BY id") != companies_before


def test_table_without_pk_skipped(env_file, demo_db, tmp_path):
    con = sqlite3.connect(demo_db)
    con.execute("CREATE TABLE notes (body TEXT)")
    con.execute("INSERT INTO notes VALUES ('secret')")
    con.commit()
    con.close()
    rule = tmp_path / "rules.csv"
    rule.write_text(
        "table_name,column_name,data_type,data_rule\n"
        "notes,body,people_fullname,japanese\n"
        "companies,tel,tel,replace_all\n"
    )
    assert main(["--env", env_file, "--rule", str(rule)]) == 2
    assert fetch_all(demo_db, "SELECT body FROM notes") == [("secret",)]
