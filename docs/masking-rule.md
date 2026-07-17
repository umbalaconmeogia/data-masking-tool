# Masking rule file

The rule file tells the tool which columns to mask and how to generate the
fake values. It is a plain CSV file, usually named `masking-rule.csv` in the
repository root (copy `masking-rule.example.csv` and edit it for your schema).
The same file format is used by every language implementation.

## File format

* RFC-4180 CSV, UTF-8, with a header row:

  ```csv
  table_name,column_name,data_type,data_rule
  ```

* One rule per row. A rule applies to exactly one `table.column`.
* Rows whose first cell starts with `#` are treated as comments and skipped.
* Extra columns after the fourth are ignored (reserved for future use).
* Declaring the same `table.column` twice is an error.

Example (matches the bundled test data):

```csv
table_name,column_name,data_type,data_rule
employees,name,people_fullname,japanese
employees,name_kana,people_fullname_kana,japanese
employees,email,email,{firstname_romaji}.{lastname_romaji}.{row_id}@example.com
employees,birthday,date,year_3
employees,tel,tel,replace_all
employees,fax,tel,replace_last_4
companies,tel,tel,replace_all
companies,fax,tel,replace_last_4
```

## Columns

| Column | Meaning |
|--------|---------|
| `table_name` | Table containing the column to mask |
| `column_name` | Column to mask |
| `data_type` | *Logical* type of the data (what the value represents — not the DB column type) |
| `data_rule` | How to generate the masking value; its meaning depends on `data_type` |

## data_type and data_rule reference

### People names

| data_type | Generated value |
|-----------|-----------------|
| `people_firstname` | A random first (given) name |
| `people_lastname` | A random last (family) name |
| `people_fullname` | Last name + first name joined with a separator |
| `people_firstname_kana` | Kana reading of the generated first name |
| `people_lastname_kana` | Kana reading of the generated last name |
| `people_fullname_kana` | Kana reading of the generated full name |

`data_rule` = a **locale**: `japanese` or `vietnamese`. A locale is any
directory `data-sample/<locale>-people/` — see [sample-data.md](sample-data.md)
for the data format and how to add your own locale.

Notes:

* Japanese full names are joined with a full-width space (U+3000), e.g.
  `山田　太郎`; other locales use an ASCII space.
* Vietnamese has no kana; the `*_kana` types return the plain name there.

### email

`data_rule` = a **pattern string**. Literal text is kept as-is and
`{placeholder}` tokens are replaced with values from the row's generated
persona:

| Placeholder | Value |
|-------------|-------|
| `{firstname}` / `{lastname}` / `{fullname}` | Generated name |
| `{firstname_kana}` / `{lastname_kana}` / `{fullname_kana}` | Kana reading |
| `{firstname_romaji}` / `{lastname_romaji}` / `{fullname_romaji}` | Romanized name, rendered lowercase ASCII |
| `{row_id}` | The row's primary key value |

Example: `{firstname_romaji}.{lastname_romaji}.{row_id}@example.com` →
`taro.yamada.42@example.com`.

Include `{row_id}` whenever the email column has a UNIQUE constraint — two
rows can otherwise receive the same generated name.

Placeholder syntax is parsed with the regular expression `\{([a-z_]+)\}`;
unknown placeholders are rejected before any masking starts.

### tel (telephone / fax)

Digits are replaced with random digits; **every non-digit character
(`-`, `(`, `)`, spaces) is kept**, and full-width digits (`０-９`) stay
full-width. NULL or empty values are left untouched.

| data_rule | Effect |
|-----------|--------|
| `replace_all` | Replace every digit |
| `replace_last_4` | Replace only the last 4 digits (keeps area/prefix codes realistic) |

Example: `03-1234-5678` → `03-1234-9012` (`replace_last_4`).

### date (birthday etc.)

The original date is shifted by a random offset. The offset is drawn from
`[-n, +n]` in the rule's unit and is never 0, so the value always changes.

| data_rule | Effect |
|-----------|--------|
| `year_<n>` | Shift by ±n years (month and day preserved) |
| `month_<n>` | Shift by ±n months |
| `day_<n>` | Shift by ±n days |

Notes:

* The day is clamped at month ends: `2020-01-31` shifted by +1 month becomes
  `2020-02-29`.
* Works with DATE and DATETIME columns; a time part is preserved.
* NULL/empty values and unparseable strings are left untouched.

## Row consistency (personas)

All rules for one table share **one generated persona per row**. For each row
the tool picks one fake person (last name + first name with their kana and
romaji readings), and every masked column of that row draws from it:

* `people_fullname` and `people_fullname_kana` describe the same person,
* an `email` pattern like `{firstname_romaji}.{lastname_romaji}@…` matches the
  masked name of the same row.

Consequences for the rule file:

* The table's locale is taken from its first name-type rule. Mixing two
  locales in the name rules of one table is a validation error.
* A table with only `email`/`tel`/`date` rules still gets personas, using the
  `MASK_DEFAULT_LOCALE` setting (default `japanese`) for name placeholders.

## Validation

The whole rule file is validated before any row is touched; on error the tool
reports the file, line number, and reason, and exits without writing anything.
Checked: header shape, known `data_type`, valid `data_rule` for the type,
known locale, known email placeholders, no duplicate `table.column`, no mixed
locales per table.

## Current limitations

* Target tables need a single-column primary key; tables without one are
  reported and skipped (exit code 2).
* One persona per row — a table storing two independent people in one row
  (e.g. `applicant_name` and `guarantor_name`) is not supported yet.
* `address` masking is planned but not implemented.
