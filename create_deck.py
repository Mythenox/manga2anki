from genanki import Deck, Note
from default_models import *
from create_vocab import Tango, Kanji
import random

def create_deck(deck_name: str = "output") -> Deck:
    deck = Deck(
        random.randrange(1 << 30, 1 << 31),
        deck_name,
    )

    return deck

def add_note(deck: Deck, entry: Tango | Kanji):
    if isinstance(entry, Kanji):
        note = Note(
            model=DEFAULT_MODEL_KANJI,
            fields=[
                entry.character,
                entry.reading,
                entry.eng_meaning,
                entry.context_surface,
                entry.context_reading,
            ],
            tags=None if entry.jlpt_rating is None else [f"jlpt-n{entry.jlpt_rating}"],
        )
    else:
        note = Note(
            model=DEFAULT_MODEL_VOCAB,
            fields=[
                entry.word,
                entry.reading,
                entry.eng_meaning,
                entry.excerpt,
            ],
            tags=[entry.part_of_speech] if entry.jlpt_rating is None else [entry.part_of_speech, f"jlpt-n{entry.jlpt_rating}"],
        )
    deck.add_note(note)
    


