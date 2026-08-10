from rhoknp import Morpheme
from manga2anki.util.inflect import lemmatize_surface, lemmatize_reading
from manga2anki.util.constants import KATAKANA, KATAKANA_TO_HIRAGANA, VOICEABLE_HIRAGANA, VOICEABLE_KATAKANA

class Tango:
    def __init__(
            self,
            parent_morpheme: Morpheme,
            part_of_speech: str,
            eng_meaning: str,
            jlpt_level: int
    ) -> None:
        self.surface = lemmatize_surface(parent_morpheme)
        self.reading = lemmatize_reading(parent_morpheme)
        self.excerpt = parent_morpheme.clause.text
        self.part_of_speech = part_of_speech
        self.eng_meaning = eng_meaning
        self.jlpt_level = jlpt_level
    
    def __repr__(self) -> str:
        return "{" + f"word={self.surface}, reading={self.reading}, type={self.part_of_speech}, JLPT N{self.jlpt_level}" + "}"
    
    
class Kanji:
    def __init__(
            self,
            parent_morpheme: Morpheme,
            surface: str,
            eng_meanings: str,
            possible_readings: list[str],
            jlpt_level: int,
            index: int
    ) -> None:
        self.surface: str = surface
        self.eng_meanings = eng_meanings
        self.possible_readings = possible_readings
        self.jlpt_level = jlpt_level
        self.context_surface = lemmatize_surface(parent_morpheme)
        self.context_reading = lemmatize_reading(parent_morpheme)
        self.excerpt = parent_morpheme.clause.text
        self.index = index
        self.inferred_reading = self.infer_reading()

    # what to do in the case of words like 日々?
    
    def infer_reading(self) -> str:
        """Infers the reading of a character based on its possible readings
        Ex: Returns げん for 現 as it appears in the morpheme 現象."""
        readings_with_mutations = add_mutations(self.possible_readings, self.index)
        # only consider the readings that appear in the reading of the morpheme to which the kanji belongs
        # e.g. do not consider あらわれ.る as a potential reading of 現 in 現象
        candidates = [
            to_hiragana(reading)
            for reading in readings_with_mutations
            if to_hiragana(reading) in self.context_reading
        ]
        if len(candidates) == 1:
            return candidates[0]
        for reading in candidates:
            if self.index == 0:
                if self.context_reading.startswith(reading):
                    remaining = self.context_reading.removeprefix(reading)
                    # if there isn't at least 1 character remaining per remaining kanji (len(self.surface) - 1), it is invalid
                    if len(remaining) >= len(self.surface) - 1:
                        return reading
            elif self.index == len(self.surface) - 1:
                if self.context_reading.endswith(reading):
                    remaining = self.context_reading.removesuffix(reading)
                    # if there isn't at least 1 character remaining per remaining kanji (len(self.surface) - 1), it is invalid
                    if len(remaining) >= len(self.surface) - 1:
                        return reading
            else:
                # in this case, the reading must be contained a substring not starting at the beginning or ending at the end of the original string.
                reading_substring: str = self.context_reading[1:-1]
                if len(reading) > len(reading_substring):
                    raise Exception("big oopsie has occurred") # hopefully this isn't even possible
                if reading in reading_substring:
                    return reading
        # the below is executed in the case of 熟字訓 such as 今日, where the individual character readings
        # do not comprise the reading of the morpheme itself
        return self.context_reading 

    
    def __repr__(self) -> str:
        return "{" + f"character={self.surface}, reading={self.inferred_reading}, context={self.context_surface}, JLPT N{self.jlpt_level}" + "}"


def add_mutations(readings: list[str], index: int) -> list[str]:
    mutated_readings = []
    if index == 0:
        # apply sokuon
        for reading in readings:
            mutated_readings.append(reading)
            if (
                reading[-1] == "つ" or 
                reading[-1] == "ち" or
                reading[-1] == "く"
            ):
                mutation = reading[:-1] + "っ"
                mutated_readings.append(mutation)
            elif (
                reading[-1] == "ツ" or
                reading[-1] == "チ" or
                reading[-1] == "ク"
            ):
                mutation = reading[:-1] + "ッ"
                mutated_readings.append(mutation)
    else:
        # apply rendaku
        for reading in readings:
            mutated_readings.append(reading)
            if reading[0] in VOICEABLE_HIRAGANA:
                mutation = f"{chr(ord(reading[0]) + 1)}" + reading[1:]
                mutated_readings.append(mutation)
                if reading[0] in {"は", "ひ", "ふ", "へ", "ほ"}:
                    mutation = f"{chr(ord(reading[0]) + 2)}" + reading[1:]
                    mutated_readings.append(mutation)
            elif reading[0] in VOICEABLE_KATAKANA:
                mutation = f"{chr(ord(reading[0]) + 1)}" + reading[1:]
                mutated_readings.append(mutation)
                if reading[0] in {"ハ", "ヒ", "フ", "ヘ", "ホ"}:
                    mutation = f"{chr(ord(reading[0]) + 2)}" + reading[1:]
                    mutated_readings.append(mutation)
                
    return mutated_readings

def to_hiragana(reading: str) -> str:
    return "".join(KATAKANA_TO_HIRAGANA[ch] if ch in KATAKANA else ch for ch in reading)