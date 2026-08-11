from rhoknp import Morpheme
from manga2anki.core.vocab import Tango, Kanji
from manga2anki.models.word_sense import WSDEngine, MorphemeDatum
from manga2anki.util.constants import KANJI, JA_SYMBOLS
import pandas as pd
from manga2anki.util.inflect import eng_pos, lemmatize_surface, lemmatize_reading
from jamdict import Jamdict
from jamdict.kanjidic2 import Character
from importlib import resources

def batch_create_kanji(
        morphemes: list[Morpheme],
        unique_kanji: set[str] = set(),
        jlpt_min: int = 5,
        jlpt_max: int = 1,
    ) -> list[Kanji]:
    kanji_csv_path = resources.files("manga2anki.assets").joinpath("jlpt_kanji_all.csv")
    with resources.as_file(kanji_csv_path) as path:
        df = pd.read_csv(path)

    jam = Jamdict()
    passed_kanji: list[Kanji] = []

    for morpheme in morphemes:
        result = jam.lookup(lemmatize_surface(morpheme))
        present_chars: list[tuple[int, Character]] = [
            (index, char) 
            for index, char in enumerate(result.chars)
            if str(char) in morpheme.surf
        ]

        for index, char in present_chars:
            row = df.query(f"Kanji == '{str(char)}'")
            if row.empty:
                jlpt_level = 0
            else:
                jlpt_level = row["Level"].item()

            if (jlpt_max <= jlpt_level <= jlpt_min) or jlpt_level == 0:
                if str(char) not in unique_kanji:
                    eng_meanings: str = ", ".join(char.meanings(english_only=True))
                    kun_readings = [r.value for r in char.rm_groups[0].readings if r.r_type == 'ja_kun']
                    on_readings = [r.value for r in char.rm_groups[0].readings if r.r_type == 'ja_on']
                    possible_readings = kun_readings + on_readings

                    passed_kanji.append(
                        Kanji(
                            parent_morpheme = morpheme,
                            surface = str(char),
                            eng_meanings = eng_meanings,
                            possible_readings = possible_readings,
                            jlpt_level = jlpt_level,
                            index = index
                        )
                    )
                    unique_kanji.add(str(char))

    return passed_kanji

def batch_create_tango(
        morphemes: list[Morpheme],
        wsd_engine: WSDEngine,
        unique_morpheme_data: set[MorphemeDatum] = set(),
        jlpt_min: int = 5,
        jlpt_max: int = 1,
    ) -> list[Tango]:
    vocab_csv_path = resources.files("manga2anki.assets").joinpath("jlpt_vocab_all_cleaned.csv")
    with resources.as_file(vocab_csv_path) as path:
        df = pd.read_csv(path)

    morpheme_data: list[MorphemeDatum] = []

    for morpheme in morphemes:
        # including する introduces a ton of redundancy
        if len(morpheme.surf) == 1 and morpheme.surf not in KANJI:
            # filters out 1 character garbage
            continue

        bad_symbol_present = False
        for char in morpheme.surf:
            if char not in JA_SYMBOLS:
                bad_symbol_present = True
                break
        if bad_symbol_present:
            continue

        if not is_vocab(morpheme) or morpheme.lemma == "する":
            continue

        # fetch jlpt level of morpheme and filter those that don't pass the filter
        row = df.query(f"expression == '{lemmatize_surface(morpheme)}' and reading == '{lemmatize_reading(morpheme)}'")
        if row.empty:
            # try again with just kana
            # for example, 奢る does not appear in the csv, but おごる does
            row = df.query(f"expression == '{lemmatize_surface(morpheme)}' and reading == '{lemmatize_reading(morpheme)}'")
        if row.empty:
            jlpt_level = 0
        else:
            try:
                jlpt_level = row["level"].item()
            except ValueError:
                """in the case that there are multiple entries with the same surface and reading,
                it's likely the case of a morpheme also being able to function as a suffix,
                such as how 目 functions as a suffix in 2日.
                However, affixes are filtered out by is_vocab(), so these will be ignored and
                the word with the lower JLPT level of the (hopefully only) 2 will be used
                as a rough heuristic."""

                levels = [level for index, level in row["level"].items()]
                jlpt_level = max(levels) # i.e. chooses N5 instead of N4 for 目

        if (jlpt_max <= jlpt_level <= jlpt_min) or jlpt_level == 0:
            morpheme_datum = MorphemeDatum(morpheme, jlpt_level)
            if morpheme_datum not in unique_morpheme_data:
                morpheme_data.append(morpheme_datum)
                unique_morpheme_data.add(morpheme_datum)

    # happens in the case that all the input was garbage and filtered out
    if len(morpheme_data) == 0:
        return []

    sense_results = wsd_engine.predict_word_sense(morpheme_data)
    tango_batch: list[Tango] = []
    for sense_result in sense_results:
        morpheme = sense_result["morpheme_datum"].morpheme
        pos = eng_pos(morpheme)
        best_sense = sense_result["best_sense"]
        jlpt_level = sense_result["morpheme_datum"].jlpt_level

        tango_batch.append(Tango(morpheme, pos, best_sense, jlpt_level))

    return tango_batch

def is_vocab(morpheme: Morpheme) -> bool:
    acceptable_pos = {"名詞", "動詞", "形容詞", "副詞", "連体詞", "接続詞"}
    unacceptable_subpos = {"地名", "人名"}
    return (
        morpheme.pos in acceptable_pos and
        morpheme.subpos not in unacceptable_subpos
    )

def is_kango(word: str) -> bool:
    for character in word:
        if character not in KANJI:
            return False
    return True