#!/usr/bin/env python3
"""Convert the raw Vietnamese name .txt lists into normalized name CSVs.

Output: <out>/lastname.csv and <out>/firstname.csv (male + female merged,
with a gender column), header ``name,kana,romaji[,gender]``.
Vietnamese has no kana, so kana = the plain name. Romaji = the name with
diacritics folded to ASCII, spaces removed, lowercased.
"""
import argparse
import csv
import os
import unicodedata


def fold_romaji(name):
    name = name.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", name)
    ascii_only = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return ascii_only.replace(" ", "").lower()


def read_names(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "data-sample", "vietnamese-people"
    )
    parser.add_argument("--raw", default=os.path.join(default_dir, "raw"))
    parser.add_argument("--out", default=default_dir)
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    lastnames = read_names(os.path.join(args.raw, "vietnamese-lastname.txt"))
    with open(os.path.join(args.out, "lastname.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "kana", "romaji"])
        for name in lastnames:
            writer.writerow([name, name, fold_romaji(name)])
    print(f"lastname.csv: wrote {len(lastnames)} rows")

    firstnames = [
        (name, "male")
        for name in read_names(os.path.join(args.raw, "vietnamese-firstname-male.txt"))
    ] + [
        (name, "female")
        for name in read_names(os.path.join(args.raw, "vietnamese-firstname-female.txt"))
    ]
    with open(os.path.join(args.out, "firstname.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "kana", "romaji", "gender"])
        for name, gender in firstnames:
            writer.writerow([name, name, fold_romaji(name), gender])
    print(f"firstname.csv: wrote {len(firstnames)} rows")


if __name__ == "__main__":
    main()
