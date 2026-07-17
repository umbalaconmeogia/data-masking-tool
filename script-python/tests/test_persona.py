import os
import random

import pytest

from masking_tool.persona import PersonaFactory

DATA_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data-sample")
)


@pytest.fixture
def factory():
    return PersonaFactory(DATA_DIR, random.Random(42))


def test_japanese_persona_consistent(factory):
    persona = factory.create("japanese")
    assert persona.fullname == persona.lastname + "　" + persona.firstname
    assert persona.fullname_kana == persona.lastname_kana + "　" + persona.firstname_kana
    assert persona.firstname_romaji.isascii()
    assert persona.lastname_romaji.isascii()


def test_japanese_kana_pairs_with_kanji(factory):
    # The kana/romaji of a persona must come from the same source rows as the names.
    source = factory._source("japanese")
    persona = factory.create("japanese")
    assert any(
        e.name == persona.lastname and e.kana == persona.lastname_kana
        and e.romaji == persona.lastname_romaji
        for e in source.lastnames
    )
    assert any(
        e.name == persona.firstname and e.kana == persona.firstname_kana
        and e.romaji == persona.firstname_romaji
        for e in source.firstnames
    )


def test_vietnamese_persona(factory):
    persona = factory.create("vietnamese")
    assert persona.fullname == persona.lastname + " " + persona.firstname
    assert persona.firstname_kana == persona.firstname  # no kana in Vietnamese
    assert persona.firstname_romaji.isascii()


def test_as_dict_lowercases_romaji(factory):
    persona = factory.create("vietnamese")
    values = persona.as_dict(12)
    assert values["row_id"] == "12"
    assert values["firstname_romaji"] == values["firstname_romaji"].lower()


def test_seeded_rng_reproducible():
    p1 = PersonaFactory(DATA_DIR, random.Random(7)).create("japanese")
    p2 = PersonaFactory(DATA_DIR, random.Random(7)).create("japanese")
    assert p1 == p2
