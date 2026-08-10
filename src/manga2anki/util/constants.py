HIRAGANA: set[str] = {
    chr(code) 
    for code in range(0x3040, 0x309F)
    if code not in {0x3040, 0x3098, 0x3097}
}

KATAKANA: set[str] = {
    chr(code)
    for code in range(0x30A0, 0x30FF)
}

KATAKANA_TO_HIRAGANA: dict[str, str] = {
    chr(code_ktk): chr(code_hrg)
    for code_hrg, code_ktk in zip(range(0x3041, 0x3097), range(0x30A1, 0x30F7))
}

VOICEABLE_HIRAGANA: set[str] =  {
    "か", "き", "く", "け", "こ",
    "さ", "し", "す", "せ", "そ",
    "た", "ち", "つ", "て", "と",
    "は", "ひ", "ふ", "へ", "ほ"
}

VOICEABLE_KATAKANA: set[str] = {
    "カ", "キ", "ク", "ケ", "コ",
    "サ", "シ", "ス", "セ", "ソ",
    "タ", "チ", "ツ", "テ", "ト",
    "ハ", "ヒ", "フ", "ヘ", "ホ"
}

FILLER: set[str] = {
    "て", "く",
}

KANJI: set[str] = {
    chr(code)
    for code in range(0x4E00, 0x9FFF)
}