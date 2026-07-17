import datetime
import random

import pytest

from masking_tool.generators import mask_date, mask_tel, render_pattern


@pytest.fixture
def rng():
    return random.Random(1)


class TestTel:
    def test_null_and_empty_untouched(self, rng):
        assert mask_tel(None, "replace_all", rng) is None
        assert mask_tel("", "replace_all", rng) == ""

    def test_formatting_preserved(self, rng):
        masked = mask_tel("03-1234-5678", "replace_all", rng)
        assert masked[2] == "-" and masked[7] == "-"
        assert len(masked) == 12
        assert masked.replace("-", "").isdigit()

    def test_replace_last_4_keeps_prefix(self, rng):
        masked = mask_tel("03-1234-5678", "replace_last_4", rng)
        assert masked.startswith("03-1234-")
        assert masked[8:].isdigit()

    def test_fullwidth_digits(self, rng):
        masked = mask_tel("０３-１２", "replace_all", rng)
        assert all(c in "０１２３４５６７８９" for c in masked if c != "-")

    def test_no_digits_untouched(self, rng):
        assert mask_tel("n/a", "replace_all", rng) == "n/a"


class TestDate:
    def test_null_untouched(self, rng):
        assert mask_date(None, "year_3", rng) is None
        assert mask_date("", "year_3", rng) == ""

    def test_string_date_shifted_within_range_never_zero(self):
        rng = random.Random(7)
        original = "1990-06-15"
        for _ in range(200):
            masked = mask_date(original, "year_3", rng)
            year = int(masked[:4])
            assert masked != original
            assert 1987 <= year <= 1993
            assert masked[4:] == "-06-15"

    def test_day_shift(self):
        rng = random.Random(7)
        for _ in range(50):
            masked = mask_date("2020-01-10", "day_5", rng)
            day = int(masked[8:10])
            assert masked != "2020-01-10"
            assert 5 <= day <= 15

    def test_month_end_clamped(self):
        rng = random.Random(0)
        for _ in range(100):
            masked = mask_date("2020-01-31", "month_1", rng)
            assert masked in ("2019-12-31", "2020-02-29")

    def test_datetime_object_time_preserved(self, rng):
        original = datetime.datetime(1990, 6, 15, 12, 30, 45)
        masked = mask_date(original, "day_2", rng)
        assert isinstance(masked, datetime.datetime)
        assert masked.time() == original.time()
        assert masked.date() != original.date()

    def test_date_object(self, rng):
        original = datetime.date(1990, 6, 15)
        masked = mask_date(original, "month_2", rng)
        assert isinstance(masked, datetime.date)
        assert masked != original

    def test_datetime_string_time_part_preserved(self, rng):
        masked = mask_date("1990-06-15 08:00:00", "year_1", rng)
        assert masked.endswith(" 08:00:00")
        assert masked[:4] in ("1989", "1991")

    def test_unparseable_untouched(self, rng):
        assert mask_date("15/06/1990", "year_3", rng) == "15/06/1990"


def test_render_pattern():
    values = {"firstname_romaji": "hanako", "lastname_romaji": "sato", "row_id": "7"}
    assert render_pattern(
        "{firstname_romaji}.{lastname_romaji}.{row_id}@example.com", values
    ) == "hanako.sato.7@example.com"
    assert render_pattern("plain@example.com", values) == "plain@example.com"
