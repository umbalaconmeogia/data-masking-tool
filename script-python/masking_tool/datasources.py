"""Locale name-data loading.

A locale is a directory ``<data_dir>/<locale>-people/`` containing
``lastname.csv`` and ``firstname.csv`` with header ``name,kana,romaji``
(extra columns such as ``gender`` are ignored).
"""
import csv
import os
from dataclasses import dataclass


@dataclass
class NameEntry:
    name: str
    kana: str
    romaji: str


class DataSourceError(Exception):
    pass


def discover_locales(data_dir):
    """Locales available under data_dir (directories named <locale>-people)."""
    locales = set()
    if not os.path.isdir(data_dir):
        return locales
    for entry in os.listdir(data_dir):
        if entry.endswith("-people") and os.path.isdir(os.path.join(data_dir, entry)):
            locale_dir = os.path.join(data_dir, entry)
            if os.path.isfile(os.path.join(locale_dir, "lastname.csv")) and \
                    os.path.isfile(os.path.join(locale_dir, "firstname.csv")):
                locales.add(entry[: -len("-people")])
    return locales


def _load_csv(path):
    entries = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for field_name in ("name", "kana", "romaji"):
            if field_name not in (reader.fieldnames or []):
                raise DataSourceError(f"{path}: missing column '{field_name}'")
        for row in reader:
            if row["name"]:
                entries.append(NameEntry(row["name"], row["kana"], row["romaji"]))
    if not entries:
        raise DataSourceError(f"{path}: no data rows")
    return entries


class NameSource:
    """In-memory name pools for one locale."""

    def __init__(self, data_dir, locale):
        locale_dir = os.path.join(data_dir, f"{locale}-people")
        if not os.path.isdir(locale_dir):
            raise DataSourceError(
                f"no sample data for locale '{locale}' (expected {locale_dir})"
            )
        self.locale = locale
        self.lastnames = _load_csv(os.path.join(locale_dir, "lastname.csv"))
        self.firstnames = _load_csv(os.path.join(locale_dir, "firstname.csv"))
