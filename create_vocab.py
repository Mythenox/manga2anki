from functools import cached_property
from constants import HIRAGANA, KATAKANA, KATAKANA_TO_HIRAGANA, KANJI
from infer import infer_reading
from rhoknp import Morpheme, Phrase

# filter out vocab with jlpt_rating < jlpt_filter if "n{i}" passed from command line, where i in {1,2,3,4}

class Tango:
    def __init__(
            self,
            morpheme: Morpheme,
            part_of_speech: str
    ) -> None:
        self.surface = morpheme.lemma
        self.excerpt = morpheme.phrase.text
        self.part_of_speech = part_of_speech

        if can_inflect(morpheme):
            self.reading = deinflect_reading(morpheme)
        else:
            self.reading = morpheme.reading

    @cached_property
    def eng_meaning(self):
        if self.jisho_html is None:
            return None
        return get_tango_english_meaning(self.jisho_html)
    
    @cached_property
    def jlpt_rating(self):
        if self.jisho_html is None:
            return None
        return get_tango_jlpt_rating(self.jisho_html)
    
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
    

def create_vocab(
        morpheme: Morpheme,
        kanji_mode: bool = False,
) -> Tango | list[Kanji] | None:
    # run in kanji mode if "-k" passed from command line
    # can return a single Tango, list of Kanji, empty list, or None
    if kanji_mode:
        if morpheme.can_inflect and morpheme.surface != morpheme.dictionary_form:
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
        return kanji_list
    if is_vocab(morpheme):
        return Tango(
            morpheme,
            eng_pos(morpheme)
        )
    return None

def is_vocab(morpheme: Morpheme) -> bool:
    acceptable_pos = {"名詞", "動詞", "形容詞", "副詞", "連体詞", "接続詞"}
    unacceptable_subpos = {"地名", "人名"}
    return (
        morpheme.pos in acceptable_pos and
        morpheme.subpos not in unacceptable_subpos
    )

def can_inflect(morpheme: Morpheme) -> bool:
    return (
        morpheme.pos == "動詞" or
        (
            morpheme.pos == "形容詞" and
            "イ形容詞" in morpheme.conjtype
        )
    )

def trim_na_adj(morpheme: Morpheme) -> str:
    if morpheme.surf[-1] == "な" or morpheme.surf[-1] == "に":
        return morpheme.surf[:-1]
    return morpheme.surf

def eng_pos(morpheme: Morpheme) -> str:
    match morpheme.pos:
        case "名詞":
            return "noun"
        case "動詞":
            return "verb"
        case "形容詞":
            if "イ形容詞" in morpheme.conjtype:
                return "i-adjective"
            return "na-adjective"
        case "副詞":
            return "adverb"
        case "連体詞":
            return "adnominal adjective"
        case _:
            return "conjunction"

def deinflect_reading(morpheme: Morpheme) -> str:
    # only types being passed to this function are verbs and i-adjectives
    uninflected_part: str = morpheme.reading

    if morpheme.pos == "動詞":
        # for some reason morpheme.reading == 来る and 為る for 来る and 為る respectively..?
        if morpheme.lemma == "来る":
            return "くる"
        
        dictionary_form_endings: list[str] = ["う", "く", "す", "つ", "ぬ", "む", "る"]
        if morpheme.reading[-1] in dictionary_form_endings:
            return morpheme.reading # in this case, the word must already be in dictionary form

        if morpheme.lemma in ["する", "くる"]:
            return morpheme.lemma
        if (
            "未然形" in morpheme.conjform or
            ("連用形" in morpheme.conjform and "子音動詞" in morpheme.conjtype) or
            ("テ形" in morpheme.conjform and "母音動詞" in morpheme.conjtype) or
            ("タ形" in morpheme.conjform and "母音動詞" in morpheme.conjtype)
        ):
            # i.e. 行かない (1), 行きたい (2)
            # form will be ~[か,ら,た,さ,ま,わ,な] or ~[き,り,ち,し,み,い,に] or ~[き,り,ち,し,み,い,に] + て
            uninflected_part = morpheme.reading[:-1]
            return uninflected_part + morpheme.lemma[-1]

        # want to, for example, extract the そろ from そろった
        for i in range(len(morpheme.reading)):
            if morpheme.reading[i] == "っ":
                uninflected_part = morpheme.reading[:i]

        # attach the okurigana from the lemma, i.e. the う from 揃う (そろう)
        for i in range(len(morpheme.surf)):
            if morpheme.surf[i] != morpheme.lemma[i]:
                return uninflected_part + morpheme.lemma[i:]

        # in this case, uninflected_part is a proper substring of the lemma, so it's just missing the last character
        return uninflected_part + morpheme.lemma[-1] 
    # otherwise is i-adjective
    elif morpheme.pos == "形容詞" and "イ形容詞" in morpheme.conjtype:
        if morpheme.reading[-1] == "い":
            # is already in lemmatized form in this case
            return morpheme.reading
        if "タ形" in morpheme.conjform:
            # form will be ~かった
            uninflected_part = morpheme.reading[:-3]
        elif "テ形" in morpheme.conjform:
            # form will be ~くて
            uninflected_part = morpheme.reading[:-2]
        elif "連用" in morpheme.conjform:
            # form will be ~く
            uninflected_part: str = morpheme.reading[:-1]
        return uninflected_part + "い"
    return morpheme.reading

def is_kango(word: str) -> bool:
    for character in word:
        if character not in KANJI:
            return False
    return True