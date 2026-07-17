# masking_tool (Python)

Python implementation of the data masking tool.

```bash
pip install -r requirements.txt   # PyMySQL and/or psycopg — only the driver you use is imported
python -m masking_tool --env ../.env --rule ../masking-rule.csv --dry-run
```

## CLI

```
python -m masking_tool [--env PATH] [--rule PATH] [--dry-run]
                       [--tables t1,t2] [--backup PATH]
                       [--batch-size N] [--seed N] [--data-dir PATH]
```

| Option | Meaning |
|--------|---------|
| `--env` | Path to `.env` (default `.env`) |
| `--rule` | Path to rule CSV (default `masking-rule.csv`) |
| `--dry-run` | Generate values and print a summary; write nothing |
| `--tables` | Comma-separated subset of rule tables to process |
| `--backup` | Write an original→masked mapping CSV (header `table_name,column_name,pk_value,original_value,new_value`). **Contains real data — protect it.** |
| `--batch-size` | Rows per fetch/update batch (default 500, or `MASK_BATCH_SIZE`) |
| `--seed` | Random seed for reproducible output (or `MASK_SEED`) |
| `--data-dir` | Sample data directory (default `../data-sample`, or `MASK_DATA_DIR`) |

Exit codes: `0` success · `1` configuration/connection error · `2` finished but
some tables were skipped (e.g. no single-column primary key).

## .env format

`KEY=VALUE` lines. Parser rules (a PHP port must implement these identically):
skip blank lines and lines starting with `#`; split on the first `=`; trim
whitespace around key and value; strip one pair of matching single or double
quotes around the value; no variable interpolation, no escapes, no multi-line
values.

Keys: `DB_DRIVER` (`mysql` | `pgsql` | `sqlite`), `DB_HOST`, `DB_PORT`,
`DB_NAME` (file path for sqlite), `DB_USER`, `DB_PASSWORD`, `DB_CHARSET`
(mysql only), plus optional `MASK_DEFAULT_LOCALE`, `MASK_BATCH_SIZE`,
`MASK_DATA_DIR`, `MASK_SEED`.

## Rule file format

CSV with header `table_name,column_name,data_type,data_rule`. Rows whose first
cell starts with `#` are comments; extra columns are ignored (reserved for
future use).

### data_type / data_rule

| data_type | data_rule | Result |
|-----------|-----------|--------|
| `people_firstname`, `people_lastname`, `people_fullname` | a locale: `japanese` \| `vietnamese` | Random name from the locale's pools |
| `people_firstname_kana`, `people_lastname_kana`, `people_fullname_kana` | same locale | Matching kana reading (for Vietnamese: the plain name — the language has no kana) |
| `email` | pattern, e.g. `{firstname_romaji}.{lastname_romaji}.{row_id}@example.com` | Pattern with `{placeholder}` tokens replaced |
| `tel` | `replace_all` \| `replace_last_4` | Digits replaced with random digits (last 4 only for `replace_last_4`); formatting characters and full/half width are preserved; NULL/empty untouched |
| `date` | `year_<n>` \| `month_<n>` \| `day_<n>` | Original date shifted by a random non-zero offset within ±n years/months/days; day is clamped at month ends; time part preserved; NULL untouched |

Email placeholders: `{firstname}`, `{lastname}`, `{fullname}`, `{firstname_kana}`,
`{lastname_kana}`, `{fullname_kana}`, `{firstname_romaji}`, `{lastname_romaji}`,
`{fullname_romaji}` (romaji render lowercase), `{row_id}` (the row's primary key
value — include it when the column has a UNIQUE constraint). Placeholder syntax
is parsed with the regex `\{([a-z_]+)\}`.

### Row consistency

All rules for one table share **one persona per row**: fullname, kana and any
derived email all describe the same fake person. The table's locale is taken
from its first name-type rule; a table mixing two locales in name rules is a
validation error. Tables with only email/tel/date rules use
`MASK_DEFAULT_LOCALE` (default `japanese`).

Japanese fullnames join lastname + firstname with a full-width space (U+3000);
other locales use an ASCII space.

## Sample data format

A locale is a directory `data-sample/<locale>-people/` with `lastname.csv` and
`firstname.csv`, header `name,kana,romaji` (extra columns ignored). Add your
own locale by dropping in a folder — no code change needed.

Converters (regenerate the shipped CSVs from the raw sources):

```bash
python tools/convert_japan_name_data.py        # from test_data_japan.sqlite (default 5000 rows/file, --limit 0 = all)
python tools/convert_vietnamese_name_data.py   # from the raw .txt lists
python tools/generate_test_data.py             # regenerate docker/test-data CSVs + init/schema SQL
```

## Limitations (v1)

* Tables need a single-column primary key; others are reported and skipped.
* `address` masking is not implemented yet (planned: sourced from `jp_address`
  in `test_data_japan.sqlite` via indexed random access).
* One persona per row — tables holding two independent people per row are not
  supported yet.

## Tests

```bash
python -m pytest tests/
```

The integration test builds a temporary SQLite database from
`tests/fixtures/schema-sqlite.sql` plus the shared `docker/test-data/*.csv`
files, and runs the full CLI against it.
