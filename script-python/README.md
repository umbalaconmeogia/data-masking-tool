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

## File formats

The `.env`, rule-file and sample-data formats are shared with the future PHP
implementation and documented centrally:

* [../docs/masking-rule.md](../docs/masking-rule.md) — rule file: data types, data rules, email patterns, row consistency
* [../docs/configuration.md](../docs/configuration.md) — `.env` keys and parser rules
* [../docs/sample-data.md](../docs/sample-data.md) — locale name-pool format and converters

## Tools

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
