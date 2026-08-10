from rhoknp import Morpheme
from manga2anki.core.vocab import Tango, Kanji
from manga2anki.core.word_sense import best_word_senses, MorphemeDatum
from manga2anki.util.constants import KANJI
import pandas as pd
from manga2anki.util.inflect import eng_pos, lemmatize_surface, lemmatize_reading
from jamdict import Jamdict
from jamdict.kanjidic2 import Character
from importlib import resources

def batch_create_kanji(
        morphemes: list[Morpheme],
        jlpt_min: int = 5,
        jlpt_max: int = 1,
    ) -> list[Kanji]:
    kanji_csv_path = resources.files("manga2anki.assets").joinpath("jlpt_kanji_all.csv")
    with resources.as_file(kanji_csv_path) as path:
        df = pd.read_csv(path)

    unique_kanji: set[str] = set()
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
        jlpt_min: int = 5,
        jlpt_max: int = 1,
    ) -> list[Tango]:
    vocab_csv_path = resources.files("manga2anki.assets").joinpath("jlpt_vocab_all_cleaned.csv")
    with resources.as_file(vocab_csv_path) as path:
        df = pd.read_csv(path)

    morpheme_data: list[MorphemeDatum] = []
    unique_morpheme_lemmas: set[str] = set()

    for morpheme in morphemes:
        # including する introduces a ton of redundancy
        if is_vocab(morpheme) and morpheme.lemma != "する": 
            row = df.query(f"expression == '{lemmatize_surface(morpheme)}' and reading == '{lemmatize_reading(morpheme)}'")
            if row.empty:
                # try again with just kana
                # for example, 奢る does not appear in the csv, but おごる does
                row = df.query(f"expression == '{lemmatize_surface(morpheme)}' and reading == '{lemmatize_reading(morpheme)}'")
            if row.empty:
                jlpt_level = 0
            else:
                jlpt_level = row["level"].item()

            if (jlpt_max <= jlpt_level <= jlpt_min) or jlpt_level == 0:
                if morpheme.lemma not in unique_morpheme_lemmas:
                    morpheme_data.append(MorphemeDatum(morpheme, jlpt_level))
                    unique_morpheme_lemmas.add(morpheme.lemma)

    sense_results = best_word_senses(morpheme_data)
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