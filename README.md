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

## Documentation

* [docs/masking-rule.md](docs/masking-rule.md) — rule file format: data types, data rules, email patterns, row consistency
* [docs/configuration.md](docs/configuration.md) — `.env` connection settings and masking options
* [docs/sample-data.md](docs/sample-data.md) — name pool format, adding locales, regenerating data
* [script-python/README.md](script-python/README.md) — Python CLI options and tests
* [docker/README.md](docker/README.md) — disposable MySQL/PostgreSQL playground preloaded with test data
* [docs/requirement.md](docs/requirement.md) — original requirements

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
