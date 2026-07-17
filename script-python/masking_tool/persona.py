"""Persona generation — the row-consistency core.

One Persona is created per (table, row) and shared by every column generator
for that row, so name, kana, romaji and derived email always match.
"""
from dataclasses import dataclass

from .datasources import NameSource

# Separator between lastname and firstname in fullname columns.
FULLNAME_SEPARATORS = {"japanese": "　"}  # full-width space
DEFAULT_SEPARATOR = " "


@dataclass
class Persona:
    locale: str
    firstname: str
    lastname: str
    firstname_kana: str
    lastname_kana: str
    firstname_romaji: str
    lastname_romaji: str

    @property
    def _separator(self):
        return FULLNAME_SEPARATORS.get(self.locale, DEFAULT_SEPARATOR)

    @property
    def fullname(self):
        return self.lastname + self._separator + self.firstname

    @property
    def fullname_kana(self):
        return self.lastname_kana + self._separator + self.firstname_kana

    @property
    def fullname_romaji(self):
        return self.lastname_romaji + " " + self.firstname_romaji

    def as_dict(self, row_id):
        """Placeholder name -> value map used by email patterns."""
        return {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "fullname": self.fullname,
            "firstname_kana": self.firstname_kana,
            "lastname_kana": self.lastname_kana,
            "fullname_kana": self.fullname_kana,
            "firstname_romaji": self.firstname_romaji.lower(),
            "lastname_romaji": self.lastname_romaji.lower(),
            "fullname_romaji": self.fullname_romaji.lower(),
            "row_id": "" if row_id is None else str(row_id),
        }


class PersonaFactory:
    def __init__(self, data_dir, rng):
        self._data_dir = data_dir
        self._rng = rng
        self._sources = {}

    def _source(self, locale):
        if locale not in self._sources:
            self._sources[locale] = NameSource(self._data_dir, locale)
        return self._sources[locale]

    def create(self, locale):
        source = self._source(locale)
        last = self._rng.choice(source.lastnames)
        first = self._rng.choice(source.firstnames)
        return Persona(
            locale=locale,
            firstname=first.name,
            lastname=last.name,
            firstname_kana=first.kana,
            lastname_kana=last.kana,
            firstname_romaji=first.romaji,
            lastname_romaji=last.romaji,
        )
