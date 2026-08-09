from rhoknp import Morpheme
from create_vocab import Tango, Kanji
from word_sense import best_word_senses, MorphemeDatum
from constants import KANJI
import pandas as pd
from inflect import eng_pos, lemmatize_surface, lemmatize_reading

def batch_create_kanji(morpheme: Morpheme):
    """if morpheme.can_inflect and morpheme.surface != morpheme.dictionary_form:
        kanji_list: list[Kanji] = [
            Kanji(
                character,
                morpheme.dictionary_form,
                morpheme.deinflected_reading_form,
                morpheme.excerpt,
                morpheme.surface.index(character)
            )
            for character in morpheme.surface
            if character in KANJI
        ]
    else:
        kanji_list: list[Kanji] = [
            Kanji(
                character,
                morpheme.surf,
                morpheme.reading,
                morpheme.phrase.text,
                morpheme.surface.index(character)
            )
            for character in morpheme.surface
            if character in KANJI
        ]
    if len(kanji_list) == 0:
        return None
    return kanji_list"""
    pass

def batch_create_tango(
        morphemes: list[Morpheme],
        jlpt_min: int = 5,
        jlpt_max: int = 1,
    ) -> list[Tango]:
    df = pd.read_csv("jlpt_vocab_all_cleaned.csv")
    morpheme_data: list[MorphemeDatum] = []
    unique_morpheme_lemmas: set[str] = set()
    for morpheme in morphemes:
        # including する introduces a ton of redundancy
        if is_vocab(morpheme) and morpheme.lemma != "する": 
            print(f"Surface: {lemmatize_surface(morpheme)} Reading: {lemmatize_reading(morpheme)}")
            row = df.query(f"expression == '{lemmatize_surface(morpheme)}' and reading == '{lemmatize_reading(morpheme)}'")
            if row.empty:
                print("empty result")
                # try again with just kana
                # for example, 奢る does not appear in the csv, but おごる does
                row = df.query(f"expression == '{lemmatize_surface(morpheme)}' and reading == '{lemmatize_reading(morpheme)}'")
            if row.empty:
                print("empty result again")
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