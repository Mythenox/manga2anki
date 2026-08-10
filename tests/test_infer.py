import unittest
from src.manga2anki.util.infer import infer_reading, add_mutations

class TestInfer(unittest.TestCase):
    def test_infer_reading1(self):
        surface = "音楽"
        token_reading = "オンガク"
        possible_readings = {"kunyomi": ["たの", "この"], "onyomi": ["ガク", "ラク", "ゴウ"]}
        index = 1
        actual = infer_reading(token_reading, possible_readings, index, surface)
        expected = "ガク"
        self.assertEqual(actual, expected)

    def test_infer_reading2(self):
        surface = "優勝"
        token_reading = "ユウショウ"
        possible_readings = {"kunyomi": ["やさ", "すぐ", "まさ"], "onyomi": ["ユウ", "ウ"]}
        index = 0
        actual = infer_reading(token_reading, possible_readings, index, surface)
        expected = "ユウ"
        self.assertEqual(actual, expected)

    def test_infer_reading3(self):
        surface = "画角"
        token_reading = "ガカク"
        possible_readings = {"kunyomi": ["えが.く", "かく.する", "かぎ.る", "はかりごと", "はか.る"],
                             "onyomi": ["ガ", "カク", "エ", "カイ"]
        }
        index = 0
        actual = infer_reading(token_reading, possible_readings, index, surface)
        expected = "ガ"
        self.assertEqual(actual, expected)

    def test_add_mutations1(self):
        context = "オリガミ"
        readings = ["かみ", "シ"]
        index = 1
        actual = set(add_mutations(readings, index))
        expected = {"がみ", "ジ", "かみ", "シ"}
        self.assertSetEqual(actual, expected)

    def test_add_mutations2(self):
        context = "こいびと"
        readings = ["ひと", "ニン", "ジン"]
        index = 1
        actual = set(add_mutations(readings, index))
        expected = {"ひと", "びと", "ぴと", "ニン", "ジン"}
        self.assertSetEqual(actual, expected)
    
    def test_add_mutations3(self):
        context = "はっぴょう"
        readings = ["ハツ", "ホツ", "た.つ", "あば.く", "おこ.る", "つか.わす", "はな.つ"]
        index = 0
        actual = set(add_mutations(readings, index))
        expected = {"ハツ", "ハッ", "ホツ", "ホッ", "た.つ", "た.っ", "あば.く", "あば.っ", "おこ.る", "つか.わす", "はな.つ", "はな.っ"}
        self.assertSetEqual(actual, expected)

    def test_infer_reading_sokuon1(self):
        surface = "説得"
        token_reading = "セットク"
        possible_readings = {"kunyomi": ["と.く"], "onyomi": ["セツ", "ゼイ"]}
        index = 0
        actual = infer_reading(token_reading, possible_readings, index, surface)
        expected = "セッ"
        self.assertEqual(actual, expected)

    def test_infer_reading_voicing1(self):
        surface = "誕生日"
        token_reading = "タンジョウビ"
        possible_readings = {"kunyomi": ["ひ", "-び", "-か"], "onyomi": ["ニチ", "ジツ"]}
        index = 2
        actual = infer_reading(token_reading, possible_readings, index, surface)
        expected = "び"
        self.assertEqual(actual, expected)

    def test_infer_reading_voicing2(self):
        surface = "鉛筆"
        token_reading = "エンピツ"
        possible_readings = {"kunyomi": ["ふで"], "onyomi": ["ヒツ"]}
        index = 1
        actual = infer_reading(token_reading, possible_readings, index, surface)
        expected = "ピツ"
        self.assertEqual(actual, expected)

    def test_infer_reading_jkj1(self):
        surface = "今日"
        token_reading = "きょう"
        possible_readings = {"kunyomi": ["いま"], "onyomi": ["コン", "キン"]}
        index = 0
        actual = infer_reading(token_reading, possible_readings, index, surface)
        expected = "きょう"
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()