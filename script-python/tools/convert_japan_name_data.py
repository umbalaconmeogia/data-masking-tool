#!/usr/bin/env python3
"""Convert jp_people_name from test_data_japan.sqlite into normalized name CSVs.

Output: <out>/lastname.csv (type=1) and <out>/firstname.csv (type=2),
header ``name,kana,romaji``. Rows whose kana cannot be converted to romaji
are skipped. With --limit N, a deterministic every-k-th sample of N rows is
kept per file so the subset spans the whole alphabet.
"""
import argparse
import csv
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from masking_tool.romaji import hiragana_to_romaji, katakana_to_hiragana  # noqa: E402

FILES = {1: "lastname.csv", 2: "firstname.csv"}


def normalize_kana(kana):
    if kana is None:
        return ""
    return katakana_to_hiragana(kana.strip().replace("　", "").replace(" ", ""))


def export(con, name_type, out_path, limit):
    rows = []
    seen = set()
    query = "SELECT kanji, kana FROM jp_people_name WHERE type = ? ORDER BY id"
    for kanji, kana in con.execute(query, (name_type,)):
        kanji = (kanji or "").strip()
        kana = normalize_kana(kana)
        if not kanji or not kana:
            continue
        romaji = hiragana_to_romaji(kana)
        if romaji is None:
            continue
        key = (kanji, kana)
        if key in seen:
            continue
        seen.add(key)
        rows.append((kanji, kana, romaji))

    total = len(rows)
    if limit and total > limit:
        step = total / limit
        rows = [rows[int(i * step)] for i in range(limit)]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "kana", "romaji"])
        writer.writerows(rows)
    print(f"{out_path}: wrote {len(rows)} rows (from {total} convertible source rows)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_sqlite = os.path.join(
        os.path.dirname(__file__), "..", "..",
        "data-sample", "japan-test-data", "test_data_japan.sqlite",
    )
    default_out = os.path.join(
        os.path.dirname(__file__), "..", "..", "data-sample", "japanese-people"
    )
    parser.add_argument("--sqlite", default=default_sqlite)
    parser.add_argument("--out", default=default_out)
    parser.add_argument("--limit", type=int, default=5000,
                        help="max rows per output file, 0 = no limit (default 5000)")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    con = sqlite3.connect(args.sqlite)
    try:
        for name_type, filename in FILES.items():
            export(con, name_type, os.path.join(args.out, filename), args.limit)
    finally:
        con.close()


if __name__ == "__main__":
    main()
