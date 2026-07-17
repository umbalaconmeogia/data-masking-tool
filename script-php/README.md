# PHP implementation (planned)

The PHP port is not implemented yet. It will share all repository-level formats
with the Python implementation, so no configuration change will be needed:

* `.env` — plain KEY=VALUE (skip blank/`#` lines, split on first `=`, trim,
  strip one pair of surrounding quotes; no interpolation).
* `masking-rule.csv` — RFC-4180 CSV, header `table_name,column_name,data_type,data_rule`,
  `#`-prefixed rows are comments, extra columns ignored.
* `data-sample/<locale>-people/lastname.csv` and `firstname.csv` — header `name,kana,romaji`.
* Email patterns — `{placeholder}` tokens matched with the regex `\{([a-z_]+)\}`.

See the format specifications in [../docs/masking-rule.md](../docs/masking-rule.md),
[../docs/configuration.md](../docs/configuration.md) and
[../docs/sample-data.md](../docs/sample-data.md).
