import unittest
from src.manga2anki.util.constants import KATAKANA_TO_HIRAGANA

class TestKana(unittest.TestCase):

    def test_kana(self):
        phrase = "キャンセルラッシュ"
        actual = "".join(KATAKANA_TO_HIRAGANA[ch] for ch in phrase)
        expected = "きゃんせるらっしゅ"
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()