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

def lemmatize_reading_verb(morpheme: Morpheme) -> str:
    if morpheme.semantics is None:
        return ""
    
    try:
        lemmatized_form: str | bool = morpheme.semantics["代表表記"]
    except KeyError:
        print(f"Error: the following morpheme does not have a 代表表記 key: {morpheme.surf}")
        return ""

    # in this case, the real lemma is the value of the 可能動詞 key
    # e.g. 出せる -> {..., "可能動詞": "出す/だす"}
    if morpheme.semantics.get("可能動詞", None) is not None:
        lemmatized_form: str | bool = morpheme.semantics["可能動詞"]
    if isinstance(lemmatized_form, bool):
            return ""
    lemma_reading: str = lemmatized_form.split("/")[-1]

    return lemma_reading

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