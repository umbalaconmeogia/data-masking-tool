# data-sample

Name pools used by the masking tool to generate fake values.

## What the tool actually reads

At runtime the tool reads **only** the normalized locale CSVs:

```
japanese-people/lastname.csv      japanese-people/firstname.csv
vietnamese-people/lastname.csv    vietnamese-people/firstname.csv
```

Format: header `name,kana,romaji` (extra columns ignored). These files are
committed and complete — **you do not need anything else in this folder to
run the tool or its tests.**

## Raw source data (optional, converter input only)

The remaining content is the raw material the CSVs were generated from. It is
kept only so the CSVs can be regenerated or extended, and is never read by the
masking tool itself:

| Path | In git? | Used by |
|------|---------|---------|
| `vietnamese-people/raw/*.txt` | yes (tiny) | `script-python/tools/convert_vietnamese_name_data.py` |
| `japan-test-data/*.sqlite` | **no** (.gitignored, ~38 MB) | `script-python/tools/convert_japan_name_data.py`, `script-python/tools/generate_test_data.py` |

The Vietnamese lists originally come from
<https://github.com/umbalaconmeogia/php-test-data/tree/master/src/vietnam>.

If you need the Japanese SQLite files (only to regenerate the Japanese CSVs or
the test data, or for the planned `address` masking), download
`test_data_japan.sqlite` and `test_data_demo.sqlite` from

> https://github.com/umbalaconmeogia/yii2-test-data-japan/tree/master/demo/data

and place them in `data-sample/japan-test-data/`.
