from src.manga2anki.core.batch_create import batch_create_tango, batch_create_kanji
from src.manga2anki.util.inflect import lemmatize_reading
import unittest
from rhoknp import KNP

knp = KNP()

class TestWord(unittest.TestCase):
    def test_deinflect1(self):
        word = "します"
        morpheme = knp.apply_to_sentence(word).morphemes[0]
        actual = lemmatize_reading(morpheme)
        expected = "する"
        self.assertEqual(actual, expected)

    def test_deinflect2(self):
        sentence = "お願いします"
        morpheme = knp.apply_to_sentence(sentence).morphemes[1]
        actual = lemmatize_reading(morpheme)
        expected = "ねがう"
        self.assertEqual(actual, expected)

    def test_deinflect3(self):
        sentence = "相手を誘い、油断させる"
        morpheme = knp.apply_to_sentence(sentence).morphemes[2]
        actual = lemmatize_reading(morpheme)
        expected = "さそう"
        self.assertEqual(actual, expected)

    """def test_bulk(self):
        bulk = "おぞましく許さない行ったおいしかった食べた暑かった離されない生きて去ります"
        morphemes = knp.apply_to_sentence(bulk).morphemes
        print([m.surf for m in morphemes])
        for m in morphemes:
            print(f"{m.surf}: {lemmatize_reading(m)}")"""

    def test_irregular1(self):
        content = "来る"
        morpheme = knp.apply_to_sentence(content).morphemes[0]
        actual = lemmatize_reading(morpheme) 
        expected = "くる"
        self.assertEqual(actual, expected)

    def test_te_form1(self):
        content = "煽って"
        morpheme = knp.apply_to_sentence(content).morphemes[0]
        actual = lemmatize_reading(morpheme)
        expected = "あおる"
        self.assertEqual(actual, expected)

    def test_te_form2(self):
        content = "熱くて"
        morpheme = knp.apply_to_sentence(content).morphemes[0]
        actual = lemmatize_reading(morpheme)
        expected = "あつい"
        self.assertEqual(actual, expected)

    def test_uninflected1(self):
        # making sure words already in their dictionary form are left alone
        content = "覆う行く話す放つ死ぬ読む食べる"
        morphemes = knp.apply_to_sentence(content).morphemes
        actual = [lemmatize_reading(m) for m in morphemes]
        expected = ["おおう", "いく", "はなす", "はなつ", "しぬ", "よむ", "たべる"]
        self.assertListEqual(actual, expected)

    def test_uninflected2(self):
        content = "暑い"
        morpheme = knp.apply_to_sentence(content).morphemes[0]
        actual = lemmatize_reading(morpheme)
        expected = "あつい"
        self.assertEqual(actual, expected)

    def test_batch_create_tango1(self):
        text = "今年の大会は誰が勝敗決まる前に離席するか予想お願いします"
        morphemes = knp.apply_to_sentence(text).morphemes
        tango_batch = batch_create_tango(morphemes)
        for tango in tango_batch:
            print(f"Word: {tango.surface} JLPT Level: N{tango.jlpt_level}")

    def test_batch_create_tango2(self):
        text = "綺麗な水が静かに垂れている"
        morphemes = knp.apply_to_sentence(text).morphemes
        tango_batch = batch_create_tango(morphemes)
        for tango in tango_batch:
            print(f"Word: {tango.surface} JLPT Level: N{tango.jlpt_level}")

    def test_batch_create_kanji1(self):
        text = "綺麗な水が静かに垂れている"
        morphemes = knp.apply_to_sentence(text).morphemes
        kanji_batch = batch_create_kanji(morphemes)
        for kanji in kanji_batch:
            print(f"Word: {kanji.surface} JLPT Level: N{kanji.jlpt_level} Reading: {kanji.inferred_reading}")

if __name__ == "__main__":
    unittest.main()