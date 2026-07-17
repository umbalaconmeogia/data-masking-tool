"""Hiragana to Hepburn romaji conversion.

Used to derive the romaji column of the sample name data. Returns None for
input containing characters outside the supported kana set, so callers can
skip noisy source rows.
"""

DIGRAPHS = {
    "きゃ": "kya", "きゅ": "kyu", "きょ": "kyo",
    "しゃ": "sha", "しゅ": "shu", "しょ": "sho",
    "ちゃ": "cha", "ちゅ": "chu", "ちょ": "cho",
    "にゃ": "nya", "にゅ": "nyu", "にょ": "nyo",
    "ひゃ": "hya", "ひゅ": "hyu", "ひょ": "hyo",
    "みゃ": "mya", "みゅ": "myu", "みょ": "myo",
    "りゃ": "rya", "りゅ": "ryu", "りょ": "ryo",
    "ぎゃ": "gya", "ぎゅ": "gyu", "ぎょ": "gyo",
    "じゃ": "ja", "じゅ": "ju", "じょ": "jo",
    "ぢゃ": "ja", "ぢゅ": "ju", "ぢょ": "jo",
    "びゃ": "bya", "びゅ": "byu", "びょ": "byo",
    "ぴゃ": "pya", "ぴゅ": "pyu", "ぴょ": "pyo",
    "くゎ": "kwa", "ぐゎ": "gwa",
    "うぃ": "wi", "うぇ": "we", "うぉ": "wo",
    "ゔぁ": "va", "ゔぃ": "vi", "ゔぇ": "ve", "ゔぉ": "vo",
    "ふぁ": "fa", "ふぃ": "fi", "ふぇ": "fe", "ふぉ": "fo",
    "てぃ": "ti", "でぃ": "di", "とぅ": "tu", "どぅ": "du",
    "しぇ": "she", "ちぇ": "che", "じぇ": "je",
}

MONOGRAPHS = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "わ": "wa", "ゐ": "i", "ゑ": "e", "を": "o", "ん": "n",
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
    "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
    "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o",
    "ゃ": "ya", "ゅ": "yu", "ょ": "yo", "ゎ": "wa",
    "ゔ": "vu",
}

VOWELS = "aiueo"


def katakana_to_hiragana(text):
    """Shift katakana codepoints down to hiragana; other chars unchanged."""
    out = []
    for ch in text:
        code = ord(ch)
        if 0x30A1 <= code <= 0x30F6:  # ァ..ヶ
            out.append(chr(code - 0x60))
        else:
            out.append(ch)
    return "".join(out)


def hiragana_to_romaji(kana):
    """Convert a hiragana string to Hepburn romaji.

    Returns None if the string contains anything that cannot be converted.
    """
    if not kana:
        return None
    kana = katakana_to_hiragana(kana)
    result = []
    i = 0
    n = len(kana)
    pending_sokuon = False
    while i < n:
        ch = kana[i]
        if ch == "っ":
            pending_sokuon = True
            i += 1
            continue
        if ch == "ー":
            if not result or result[-1][-1] not in VOWELS:
                return None
            result.append(result[-1][-1])
            i += 1
            continue
        piece = None
        if i + 1 < n:
            piece = DIGRAPHS.get(kana[i : i + 2])
            if piece is not None:
                i += 2
        if piece is None:
            piece = MONOGRAPHS.get(ch)
            if piece is None:
                return None
            i += 1
        if pending_sokuon:
            # Sokuon doubles the following consonant; before ch- it becomes "t".
            if piece[0] in VOWELS:
                return None
            result.append("t" if piece.startswith("ch") else piece[0])
            pending_sokuon = False
        result.append(piece)
    if pending_sokuon:  # trailing っ
        return None
    return "".join(result)
