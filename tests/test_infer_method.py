import unittest
from src.manga2anki.core.create_cards import batch_create_kanji
from src.manga2anki.core.vocab import Kanji
from rhoknp import KNP

knp = KNP()

class TestInfer(unittest.TestCase):
    def test_infer_reading1(self):
        text = "音楽"
        morphemes = knp.apply_to_sentence(text).morphemes
        kanji = batch_create_kanji(morphemes)[1]
        actual = kanji.infer_reading()
        expected = "がく"
        self.assertEqual(actual, expected)

    def test_infer_reading2(self):
        text = "優勝"
        morphemes = knp.apply_to_sentence(text).morphemes
        kanji = batch_create_kanji(morphemes)[0]
        actual = kanji.infer_reading()
        expected = "ゆう"
        self.assertEqual(actual, expected)

    def test_infer_reading3(self):
        text = "画角"
        morphemes = knp.apply_to_sentence(text).morphemes
        kanji = batch_create_kanji(morphemes)[0]
        actual = kanji.infer_reading()
        expected = "が"
        self.assertEqual(actual, expected)

    def test_infer_reading_sokuon1(self):
        text = "説得"
        morphemes = knp.apply_to_sentence(text).morphemes
        kanji = batch_create_kanji(morphemes)[0]
        actual = kanji.infer_reading()
        expected = "せっ"
        self.assertEqual(actual, expected)

    def test_infer_reading_voicing1(self):
        text = "誕生日"
        morphemes = knp.apply_to_sentence(text).morphemes
        kanji = batch_create_kanji(morphemes)[2]
        actual = kanji.infer_reading()
        expected = "び"
        self.assertEqual(actual, expected)

    def test_infer_reading_voicing2(self):
        text = "鉛筆"
        morphemes = knp.apply_to_sentence(text).morphemes
        kanji = batch_create_kanji(morphemes)[1]
        actual = kanji.infer_reading()
        expected = "ぴつ"
        self.assertEqual(actual, expected)

    def test_infer_reading_jkj1(self):
        text = "今日"
        morphemes = knp.apply_to_sentence(text).morphemes
        kanji = batch_create_kanji(morphemes)[1]
        actual = kanji.infer_reading()
        expected = "きょう"
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()