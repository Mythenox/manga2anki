from manga2anki.core.create_cards import batch_create_tango, batch_create_kanji
from manga2anki.util.inflect import lemmatize_reading
import unittest
from rhoknp import Jumanpp

jpp = Jumanpp()

class TestWord(unittest.TestCase):
    
    """def test_bulk(self):
        bulk = "おぞましく許さない行ったおいしかった食べた暑かった離されない生きて去ります"
        morphemes = jpp.apply_to_sentence(bulk).morphemes
        print([m.surf for m in morphemes])
        for m in morphemes:
            print(f"{m.surf}: {lemmatize_reading(m)}")"""

    def test_batch_create_tango1(self):
        text = "今年の大会は誰が勝敗決まる前に離席するか予想お願いします"
        morphemes = jpp.apply_to_sentence(text).morphemes
        tango_batch = batch_create_tango(morphemes)
        for tango in tango_batch:
            print(f"Word: {tango.surface} JLPT Level: N{tango.jlpt_level}")

    def test_batch_create_tango2(self):
        text = "綺麗な水が静かに垂れている"
        morphemes = jpp.apply_to_sentence(text).morphemes
        tango_batch = batch_create_tango(morphemes)
        for tango in tango_batch:
            print(f"Word: {tango.surface} JLPT Level: N{tango.jlpt_level}")

    def test_batch_create_kanji1(self):
        text = "綺麗な水が静かに垂れている"
        morphemes = jpp.apply_to_sentence(text).morphemes
        kanji_batch = batch_create_kanji(morphemes)
        for kanji in kanji_batch:
            print(f"Word: {kanji.surface} JLPT Level: N{kanji.jlpt_level} Reading: {kanji.inferred_reading}")

if __name__ == "__main__":
    unittest.main()