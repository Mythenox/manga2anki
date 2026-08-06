# TODO: add support for slang terms? (words like ムズい aren't properly parsed)

#TODO: Fix deinflect and use it
#      Store words in deinflected form (probably use @cached_property?)

from typing import Union, Optional, List, Literal, Tuple
from sudachipy import tokenizer, dictionary, Morpheme, SplitMode, MorphemeList

from constants import KATAKANA_TO_HIRAGANA, KATAKANA, FILLER

"""
Strings that can be parsed as SplitMode
"""
SplitModeStr = Literal["A", "a", "B", "b", "C", "c"]

"""
L1, L2, L3, L4, conjugation type, conjugation form
"""
POS = Tuple[str, str, str, str, str, str]

def main():
    """images = [f"sample/yfnu7-7({i}).png" for i in range(13)]
    text_list: list[str] = get_bubble_text(images)
    tokens = []
    for dialogue in text_list:
        dialogue_tokens = tokenize_text(dialogue)
        tokens.extend(dialogue_tokens)
    print(tokens)
    print(len(tokens))"""

    mode = tokenizer.Tokenizer.SplitMode.C
    a = tokenize("本当に腕折れる", mode)
    for item in a:
        print(item.surface)
    """k = tokenize_text(k.get_base_form())[0]
    print(k.get_reading())"""
    

class Word:
    def __init__(
            self,
            morpheme: Morpheme,
            excerpt: str # text from which this token came
    ) -> None:
        self.surface: str = morpheme.surface()
        self.part_of_speech: POS = morpheme.part_of_speech()
        self.normalized_form: str = morpheme.normalized_form()
        self.dictionary_form: str = morpheme.dictionary_form()
        self.reading_form: str = to_hiragana(morpheme.reading_form())
        self.excerpt: str = excerpt

    def is_vocab(self) -> bool:
        """Returns true for nouns
        (exluding names of places (except countries) and people),
        adjectives and verbs."""
        if self.part_of_speech[0] == "名詞":
            # return false if name of location (except for countries)
            if self.part_of_speech[2] == "地名":
                return self.part_of_speech[3] == "国"
            # otherwise, return false if name of a person, true for every other noun
            return self.part_of_speech[2] != "人名"
        else:
            return (
                self.part_of_speech[0] == "動詞" or
                self.part_of_speech[0] == "副詞" or
                self.part_of_speech[0] == "形容詞" or
                self.part_of_speech[0] == "形状詞"
            )

    @property
    def eng_POS(self) -> str:
        if self.part_of_speech[0] == "名詞":
            return "noun"
        elif self.part_of_speech[0] == "動詞":
            return "verb"
        elif self.part_of_speech[0] == "副詞":
            return "adverb"
        elif self.part_of_speech[0] == "形状詞":
            return "na-adjective"
        elif self.part_of_speech[0] == "形容詞":
            return "i-adjective"
        return "auxilliary verb"

    @property
    def deinflected_reading_form(self) -> str:
        # only types being passed to this method are verbs and i-adjectives
        dictionary_form_endings: list[str] = ["う", "く", "す", "つ", "ぬ", "む", "る"]
        if self.reading_form[-1] in dictionary_form_endings:
            return self.reading_form # in this case, the word must already be in dictionary form
        uninflected_part: str = self.reading_form
        if self.eng_POS == "verb":
            if self.dictionary_form in ["する", "くる"]:
                return self.dictionary_form 
            if (
                "未然形" in self.part_of_speech[-1] or
                ("連用形" in self.part_of_speech[-1] and "五段" in self.part_of_speech[-2])
            ):
                # form will be ~[か,ら,た,さ,ま,わ,な] or ~[き,り,ち,し,み,い,に]
                uninflected_part = self.reading_form[:-1]
                return uninflected_part + self.dictionary_form[-1]

            for i in range(len(self.reading_form)):
                if self.reading_form[i] == "っ":
                    uninflected_part = self.reading_form[:i]

            for i in range(len(self.surface)):
                if self.surface[i] != self.dictionary_form[i]:
                    return uninflected_part + self.dictionary_form[i:]
            return uninflected_part + self.dictionary_form[-1] 
        # otherwise is i-adjective
        elif self.eng_POS == "i-adjective":
            if self.part_of_speech[-1] == "連用形-促音便":
                # form will be ~かっ
                uninflected_part: str = self.reading_form[:-2]
            elif self.part_of_speech[-1] == "連用形-一般":
                # form will be ~く
                uninflected_part: str = self.reading_form[:-1]
            return uninflected_part + "い"
        return self.reading_form
            
    @property
    def can_inflect(self) -> bool:
        inflectables: set[str] = {"verb", "i-adjective"}
        return self.eng_POS in inflectables
    
    def __repr__(self) -> str:
        return (
            "{surface=" + f"{self.surface}, "
            + f"l1_part={self.part_of_speech[0]}, "
            + f"base_form={self.dictionary_form}"
            + f'excerpt="{self.excerpt}'+ "}"
        )
    
    def __eq__(self, other) -> bool:
        return self.surface == other.surface and self.part_of_speech[0] == other.part_of_speech[0]
    
    def __hash__(self) -> int:
        return hash((self.surface, self.part_of_speech[0]))

def tokenize(
        text: str,
        mode: Union[SplitMode, SplitModeStr, None] = tokenizer.Tokenizer.SplitMode.C,
        out: Optional[MorphemeList] = None
) -> List[Word]:
    tokenizer_obj = dictionary.Dictionary().create()
    morphemes = tokenizer_obj.tokenize(text, mode)
    return [Word(morpheme, text) for morpheme in morphemes]

def is_inflected(m: Morpheme) -> bool:
    conjugation_form: str = m.part_of_speech()[-1].split("-")[0]
    return conjugation_form != "連体形"

def to_hiragana(reading: str) -> str:
    return "".join(KATAKANA_TO_HIRAGANA[ch] if ch in KATAKANA else ch for ch in reading)

if __name__ == "__main__":
    main()