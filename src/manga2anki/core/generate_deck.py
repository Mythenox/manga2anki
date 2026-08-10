from genanki import Deck, Note
from manga2anki.util.default_note_models import DEFAULT_MODEL_KANJI, DEFAULT_MODEL_VOCAB
from manga2anki.core.vocab import Tango, Kanji
import random

class GeneratedDeck:
    def __init__(self, deck_name: str = "output") -> None:
        self.deck = Deck(
            random.randrange(1 << 30, 1 << 31),
            deck_name,
        )

    def add_kanji_note(self, entry: Kanji):
        possible_readings_text = ", ".join(entry.possible_readings)
        note = Note(
                model=DEFAULT_MODEL_KANJI,
                fields=[
                    entry.surface,
                    possible_readings_text,
                    entry.eng_meanings,
                    entry.context_surface,
                    entry.context_reading,
                ],
                tags=None if entry.jlpt_level == 0 else [f"jlpt-n{entry.jlpt_level}"],
            )
        self.deck.add_note(note)

    def add_tango_note(self, entry: Tango):
        note = Note(
            model=DEFAULT_MODEL_VOCAB,
            fields=[
                entry.surface,
                entry.reading,
                entry.eng_meaning,
                entry.excerpt,
            ],
            tags=[entry.part_of_speech] if entry.jlpt_level == 0 else [entry.part_of_speech, f"jlpt-n{entry.jlpt_level}"],
        )
        self.deck.add_note(note)
    


