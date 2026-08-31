import torch
from transformers import AutoImageProcessor, AutoTokenizer, VisionEncoderDecoderModel
from PIL.Image import Image
import re
import jaconv
from manga2anki.util.constants import KANJI, JA_CHARS
import difflib

# problem: output like the following occurs:
# A: 思い出自体多くもない
# B: 思い出自多くもない
# want to detect this kind of thing and heuristically keep only the longer output

# compare similarity to kept_words set
# use hashing somehow to avoid doing a million operations for each sentence
# if no similar sentences, add word to set
# if similar sentences, choose most similar one
# replace sentence in kept_words with the longer of the two

class OCREngine:
    def __init__(self, device: str, model_name: str = "kha-white/manga-ocr-base") -> None:
        if device != "cpu":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device("cpu")

        self.image_processor = AutoImageProcessor.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, tokenizer_type="bert-japanese")
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name).to(self.device).half() # type: ignore

        
    def get_bubble_text(self, bubbles: list[Image]) -> list[str]:
        """Returns a list of sentences/excerpts, each coming from a different speech bubble."""
        pixel_values = self.image_processor(
            bubbles,
            return_tensors="pt",
        ).pixel_values.to(self.device).half()

        with torch.no_grad():
            generated_ids = self.model.generate( # type: ignore
                pixel_values,
                max_new_tokens=300,
                max_length=None
                ).cpu() 

        decoded_text: list[str] = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

        post_processed_text = [post_process(text) for text in decoded_text]

        filtered_text: list[str] = [
            text
            for text in post_processed_text
            if not is_garbage(text)
        ]

        return filtered_text

# only care about deletion and insertion.
# if substitution is necessary, abort and return some kind of sentinel value like -1
def edit_distance(str1: str, str2: str) -> int:
    pass

# remove stuff like "．．．", "(", "\"
def is_garbage(sentence: str) -> bool:
    # strings of 2 characters or less that have no kanji are almost always garbage
    if len(sentence) <= 2 and all(char not in KANJI for char in sentence):
        return True
    # filters out strings that contain no japanese characters
    if all(char not in JA_CHARS for char in sentence):
        return True
    return False

# this is garbage (see dedup.log), minhash time?
def fuzzy_deduplicate(sentences: list[str], threshold: float = 0.85) -> list[str]:
    # sorted by longest to shortest
    unique_sentences: list[str] = sorted(list(set(sentences)), key=len, reverse=True)
    final_sentences: list[str] = []

    for sentence1 in unique_sentences:
        is_duplicate = False

        # sentence2 is necessarily same length or longer
        for sentence2 in final_sentences:
            matcher = difflib.SequenceMatcher(lambda x: x == "．", sentence1, sentence2)

            match_length = sum(block.size for block in matcher.get_matching_blocks())

            # if sentence1 is a fuzzy proper substring, this ratio will be 1.0
            # for example, the sentence 原稿が終わってな最悪な気分  (nonsense)
            # is a fuzzy proper substring of 原稿が終わってないと最悪な気分なんですけどね
            # since the only difference making it not a (non-fuzzy) proper substring
            # is that it's missing "いと"
            coverage = match_length / len(sentence1)

            if coverage >= threshold:
                print(f"{sentence1} is a duplicate of {sentence2}")
                is_duplicate = True
                break

        if not is_duplicate:
            final_sentences.append(sentence1)

    return final_sentences

def post_process(text: str):
    spaces_removed: str = "".join(text.split())
    ellipsis_replaced: str = spaces_removed.replace("…", "...")
    periods_replaced: str = re.sub("[・.]{2,}", lambda x: (x.end() - x.start()) * ".", ellipsis_replaced)
    final_text = jaconv.h2z(periods_replaced, ascii=True, digit=True)

    return final_text
