# Configuration (.env)

Database connection and masking options live in a `.env` file in the
repository root (copy `.env.example` and edit it). The same file is read by
every language implementation.

## File format

`KEY=VALUE` lines. The parser is deliberately minimal so it behaves
identically in every language:

* Skip blank lines and lines starting with `#`.
* Split on the **first** `=`.
* Trim whitespace around key and value.
* Strip one pair of matching single or double quotes around the value.
* No variable interpolation, no escape sequences, no multi-line values.

## Database keys

| Key | Meaning |
|-----|---------|
| `DB_DRIVER` | `mysql` \| `pgsql` \| `sqlite` (sqlite is intended for testing/demo) |
| `DB_HOST` | Server host (default `127.0.0.1`) |
| `DB_PORT` | Server port (default `3306` for mysql, `5432` for pgsql) |
| `DB_NAME` | Database name; for sqlite: path to the database file |
| `DB_USER` | User name |
| `DB_PASSWORD` | Password |
| `DB_CHARSET` | MySQL only (default `utf8mb4`) |

## Masking option keys (all optional)

| Key | Meaning |
|-----|---------|
| `MASK_DEFAULT_LOCALE` | Persona locale for tables that have no name-type rule (default `japanese`) |
| `MASK_BATCH_SIZE` | Rows fetched/updated per batch (default `500`) |
| `MASK_DATA_DIR` | Path to the sample-data directory (default: the repository's `data-sample/`) |
| `MASK_SEED` | Random seed; set it to make masking output reproducible |

Command-line flags (`--batch-size`, `--seed`, `--data-dir`) override the
corresponding `.env` values.

## Example

```env
DB_DRIVER=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=my_database
DB_USER=root
DB_PASSWORD=secret
DB_CHARSET=utf8mb4

MASK_DEFAULT_LOCALE=japanese
MASK_BATCH_SIZE=500
#MASK_SEED=42
```

## Safety notes

* Run the tool only against a **copy** of your database — it overwrites data
  in place.
* `.env` and `masking-rule.csv` are `.gitignore`d; commit only the `.example`
  variants.
* The optional `--backup` mapping CSV contains the original confidential
  values; treat it with the same care as the original database (it is also
  `.gitignore`d by default).
