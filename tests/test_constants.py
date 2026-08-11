import unittest
from manga2anki.util.constants import KATAKANA_TO_HIRAGANA, JA_SYMBOLS

class TestKana(unittest.TestCase):

    def test_kana(self):
        phrase = "キャンセルラッシュ"
        actual = "".join(KATAKANA_TO_HIRAGANA[ch] for ch in phrase)
        expected = "きゃんせるらっしゅ"
        self.assertEqual(actual, expected)

    def test_numbers(self):
        text = "Ｓ"
        self.assertFalse(text in JA_SYMBOLS)

if __name__ == "__main__":
    unittest.main()