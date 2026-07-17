# Data masking tool

Masks confidential columns in a database (people's names, kana, email, tel/fax,
dates) with realistic fake data, so a production-like database can be used
safely for system development and testing.

* Rules are declared in a CSV file (`masking-rule.csv`) — which table.column to
  mask, its logical data type, and how to generate the fake value.
* DB connection settings live in a `.env` file.
* Sample name data (Japanese and Vietnamese) is included under `data-sample/`.
* All masked columns of one row are generated from a single fake "persona", so
  name, kana and a derived email address stay consistent within a row.
* Supports MySQL, PostgreSQL and SQLite.

## Quick start (Python)

```bash
cp .env.example .env                       # edit DB connection settings
cp masking-rule.example.csv masking-rule.csv   # edit rules for your schema

cd script-python
pip install -r requirements.txt            # only the driver you need is required

python -m masking_tool --dry-run           # preview, writes nothing
python -m masking_tool --backup masking-backup.csv   # mask, keeping a mapping
```

See [script-python/README.md](script-python/README.md) for the full rule/format
reference and CLI options, and [docker/README.md](docker/README.md) for a
disposable MySQL/PostgreSQL playground preloaded with test data.

## Repository layout

| Path | Purpose |
|------|---------|
| `masking-rule.example.csv` | Example masking rules (matches the test data) |
| `.env.example` | Example DB connection settings |
| `data-sample/japanese-people/` | Japanese name pools (`lastname.csv`, `firstname.csv`: name, kana, romaji) |
| `data-sample/vietnamese-people/` | Vietnamese name pools (same format; raw source lists in `raw/`) |
| `data-sample/japan-test-data/` | Raw source SQLite databases (name/address data, demo DB) |
| `script-python/` | Python implementation, converters and tests |
| `script-php/` | PHP implementation (planned — shares all the same config/data formats) |
| `docker/` | MySQL + PostgreSQL test containers preloaded with demo data |

## Warning

Run this tool only against a **copy** of your database. The optional
`--backup` mapping file contains the original confidential values — protect it
like the original database (it is `.gitignore`d by default).
