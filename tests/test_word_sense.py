import unittest
from src.manga2anki.core.word_sense import best_word_senses
from src.manga2anki.core.vocab import create_vocab, Tango, is_vocab
from rhoknp import KNP

knp = KNP()

class TestWordSense(unittest.TestCase):

    def test_word_sense(self):
        text = "今年の大会は誰が勝敗決まる前に離席するか予想お願いします"
        morphemes = [
            morpheme
            for morpheme in knp.apply_to_sentence(text).morphemes
            if is_vocab(morpheme)
        ]

        results = best_word_senses(morphemes)

        for result in results:
            print(f"Sentence: {result["morpheme"]}")
            print(f"  └─ Best English Sense: {result["best_sense"]}\n")

if __name__ == "__main__":
    unittest.main()