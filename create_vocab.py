from functools import cached_property
from constants import HIRAGANA, KATAKANA, KATAKANA_TO_HIRAGANA, KANJI
from infer import infer_reading
from rhoknp import Morpheme, Phrase
from jamdict import Jamdict
import pandas as pd
from inflect import lemmatize_surface, lemmatize_reading

# filter out vocab with jlpt_rating < jlpt_filter if "n{i}" passed from command line, where i in {1,2,3,4}

class Tango:
    def __init__(
            self,
            morpheme: Morpheme,
            part_of_speech: str,
            eng_meaning: str,
            jlpt_level: int
    ) -> None:
        self.surface = lemmatize_surface(morpheme)
        self.reading = lemmatize_reading(morpheme)
        self.excerpt = morpheme.clause.text
        self.part_of_speech = part_of_speech
        self.eng_meaning = eng_meaning
        self.jlpt_level = jlpt_level
    
    def __repr__(self) -> str:
        return "{" + f"word={self.surface}, reading={self.reading}, type={self.part_of_speech}, JLPT N{self.jlpt_rating}" + "}"
    
    
class Kanji:
    def __init__(
            self,
            character: str,
            context_surface: str,
            context_reading: str,
            excerpt: str,
            index: int
    ) -> None:
        self.character: str = character
        self.context_surface = context_surface
        self.context_reading = context_reading
        self.excerpt = excerpt
        self.index = index

    @cached_property
    def eng_meaning(self):
        if self.jisho_html is None:
            return None
        return get_kanji_english_meaning(self.jisho_html)
    
    @cached_property
    def jlpt_rating(self):
        if self.jisho_html is None:
            return None
        return get_kanji_jlpt_rating(self.jisho_html)
    
    @cached_property
    def reading(self) -> str | None:
        if self.jisho_html is None:
            return None
        possible_readings: dict[str, list[str]] | None = get_kanji_readings(self.jisho_html)
        if possible_readings is None:
            return None
        return infer_reading(
            self.context_reading,
            possible_readings,
            self.index,
            self.context_surface
        )
    
    def __repr__(self) -> str:
        return "{" + f"character={self.character}, reading={self.reading}, context={self.context_surface}, JLPT N{self.jlpt_rating}" + "}"