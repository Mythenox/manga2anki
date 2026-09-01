from manga2anki.util.inflect import lemmatize_reading
import unittest
from rhoknp import Jumanpp

jpp = Jumanpp()

class TestLemmatize(unittest.TestCase):
    def test_deinflect1(self):
        word = "します"
        morpheme = jpp.apply_to_sentence(word).morphemes[0]
        actual = lemmatize_reading(morpheme)
        expected = "する"
        self.assertEqual(actual, expected)

    def test_deinflect2(self):
        sentence = "お願いします"
        morpheme = jpp.apply_to_sentence(sentence).morphemes[1]
        actual = lemmatize_reading(morpheme)
        expected = "ねがう"
        self.assertEqual(actual, expected)

    def test_deinflect3(self):
        sentence = "相手を誘い、油断させる"
        morpheme = jpp.apply_to_sentence(sentence).morphemes[2]
        actual = lemmatize_reading(morpheme)
        expected = "さそう"
        self.assertEqual(actual, expected)

    def test_deinflect4(self):
        sentence = "ラウ君って呼ぶんだよ"
        morpheme = jpp.apply_to_sentence(sentence).morphemes[-3]
        actual = lemmatize_reading(morpheme)
        expected = "よぶ"
        self.assertEqual(actual, expected)

    def test_deinflect5(self):
        sentence = "聞いてよ"
        morpheme = jpp.apply_to_sentence(sentence).morphemes[0]
        actual = lemmatize_reading(morpheme)
        expected = "きく"
        self.assertEqual(actual, expected)

    def test_deinflect6(self):
        sentence = "出せる"
        morpheme = jpp.apply_to_sentence(sentence).morphemes[0]
        actual = lemmatize_reading(morpheme)
        expected = "だす"
        self.assertEqual(actual, expected)

    def test_irregular1(self):
        content = "来る"
        morpheme = jpp.apply_to_sentence(content).morphemes[0]
        actual = lemmatize_reading(morpheme) 
        expected = "くる"
        self.assertEqual(actual, expected)

    def test_irregular2(self):
        sentence = "どうかした"
        morpheme = jpp.apply_to_sentence(sentence).morphemes[-1]
        actual = lemmatize_reading(morpheme)
        expected = "する"
        self.assertEqual(actual, expected)

    def test_te_form1(self):
        content = "煽って"
        morpheme = jpp.apply_to_sentence(content).morphemes[0]
        actual = lemmatize_reading(morpheme)
        expected = "あおる"
        self.assertEqual(actual, expected)

    def test_te_form2(self):
        content = "熱くて"
        morpheme = jpp.apply_to_sentence(content).morphemes[0]
        actual = lemmatize_reading(morpheme)
        expected = "あつい"
        self.assertEqual(actual, expected)

    def test_uninflected1(self):
        # making sure words already in their dictionary form are left alone
        content = "覆う行く話す放つ死ぬ読む食べる"
        morphemes = jpp.apply_to_sentence(content).morphemes
        actual = [lemmatize_reading(m) for m in morphemes]
        expected = ["おおう", "いく", "はなす", "はなつ", "しぬ", "よむ", "たべる"]
        self.assertListEqual(actual, expected)

    def test_uninflected2(self):
        content = "暑い"
        morpheme = jpp.apply_to_sentence(content).morphemes[0]
        actual = lemmatize_reading(morpheme)
        expected = "あつい"
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()