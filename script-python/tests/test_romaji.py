from masking_tool.romaji import hiragana_to_romaji, katakana_to_hiragana


def test_basic():
    assert hiragana_to_romaji("やまだ") == "yamada"
    assert hiragana_to_romaji("さとう") == "satou"


def test_digraphs():
    assert hiragana_to_romaji("きょうこ") == "kyouko"
    assert hiragana_to_romaji("しゅんすけ") == "shunsuke"
    assert hiragana_to_romaji("じゅんじ") == "junji"


def test_sokuon():
    assert hiragana_to_romaji("はっとり") == "hattori"
    assert hiragana_to_romaji("まっちゃ") == "matcha"


def test_long_vowel_mark():
    assert hiragana_to_romaji("あーる") == "aaru"


def test_katakana_normalized():
    assert hiragana_to_romaji("ヤマダ") == "yamada"
    assert katakana_to_hiragana("ベリ") == "べり"


def test_noise_rejected():
    assert hiragana_to_romaji("あ/い") is None
    assert hiragana_to_romaji("あoい") is None
    assert hiragana_to_romaji("あ゛") is None
    assert hiragana_to_romaji("") is None
    assert hiragana_to_romaji("ーあ") is None
    assert hiragana_to_romaji("あっ") is None
