from rhoknp import Morpheme

def lemmatize_surface(morpheme: Morpheme) -> str:
    """Trims the だ from the lemmatized form of na-adjectives.
    Acts as the 'identity' on non-na-adjectives, i.e. just returns
    their regular lemma."""
    if eng_pos(morpheme) == "na-adjective":
        if morpheme.lemma[-1] == "だ":
            return morpheme.lemma[:-1]
    return morpheme.lemma

def lemmatize_reading(morpheme: Morpheme) -> str:
    """Trims だ from lemmatized reading of na-adjectives.
    Accepts deinflected reading of verbs/i-adjectives to make sure that
    this function acts as the identity on non-na-adjectives."""
    match morpheme.pos:
        case "動詞":
            return lemmatize_reading_verb(morpheme)
        case "形容詞":
            if "イ形容詞" in morpheme.conjtype:
                return lemmatize_reading_i_adj(morpheme)
            return lemmatize_reading_na_adj(morpheme)
        case _:
            return morpheme.reading
   
def lemmatize_reading_na_adj(morpheme: Morpheme) -> str:
        lemmatized_form = morpheme.semantics.get("代表表記")
        if isinstance(lemmatized_form, str):
            lemmatized_reading = lemmatized_form.split("/")[1]
            if lemmatized_reading[-1] == "だ":
                return lemmatized_reading[:-1]
        return morpheme.reading
    
def lemmatize_reading_i_adj(morpheme: Morpheme) -> str:
    uninflected_part: str = morpheme.reading
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

# inspect morpheme.semantics
# for the case of 走れる, 可能動詞 appears as a key in the semantics dict
# maybe the verb is in regular form iff semantics dict only has 1 key?

def lemmatize_reading_verb(morpheme: Morpheme) -> str: 
    # bugged for 聞いて? 
    # also 学ぶ? 
    # どうかした→どうかしたする?? 
    # 出せる->だせる?? 
    # 走れる -> はしれる?
    # 呼ぶ -> よぶぶ?
    # そそのかしてんの -> そそのかしてす?
    """Returns reading of lemmatized form of verb.
    Example: 刺さった -> ささる"""
    uninflected_part: str = morpheme.reading

    # for some reason morpheme.reading == 来る for 来る..?
    if morpheme.lemma == "来る":
        return "くる"
    
    dictionary_form_endings: list[str] = [
        "う", "く", "ぐ", "す",
        "つ", "ぬ", "ぶ", "む", "る",
        ]
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
        # stem will be of the form ~[か,ら,た,さ,ま,わ,な] (1) or ~[き,り,ち,し,み,い,に] (2)
        # i.e. 行かない (1), 行きたい (2)
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
            return "adnominal-adjective"
        case _:
            return "conjunction"