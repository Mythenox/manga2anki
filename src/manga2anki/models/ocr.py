from manga_ocr import MangaOcr
from PIL import Image
import transformers
import torch
from transformers import AutoImageProcessor, AutoTokenizer, VisionEncoderDecoderModel
from manga2anki.workers.cv_worker import TaggedBubble
from PIL import Image
import re
import jaconv

#TODO: use multiprocessing

class OCREngine:
    def __init__(self, device: str, model_name: str = "kha-white/manga-ocr-base") -> None:
        if device != "cpu":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device("cpu")

        self.image_processor = AutoImageProcessor.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, tokenizer_type="bert-japanese")
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name).to(self.device) # type: ignore

        

    def get_bubble_text(self, tagged_bubbles: list[TaggedBubble]) -> list[str]:
        ids: list[str] = [tagged_bubble["id"] for tagged_bubble in tagged_bubbles]
        images: list[Image.Image] = [
            Image.fromarray(tagged_bubble["img"])
            for tagged_bubble in tagged_bubbles
        ]

        pixel_values = self.image_processor(
            images,
            return_tensors="pt",
        ).pixel_values.to(self.device)

        with torch.no_grad():
            generated_ids = self.model.generate(pixel_values, max_new_tokens=300) # type: ignore

        decoded_text: list[str] = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

        post_processed_text = [post_process(text) for text in decoded_text]

        return post_processed_text

    def get_text(self, tagged_bubbles: list[TaggedBubble]) -> list[str]:
        ids: list[str] = [tagged_bubble["id"] for tagged_bubble in tagged_bubbles]
        images: list[Image.Image] = [
            Image.fromarray(tagged_bubble["img"])
            for tagged_bubble in tagged_bubbles
        ]

        pixel_values = self.image_processor(
            images,
            return_tensors="pt",
        ).pixel_values.to(self.device)

        with torch.no_grad():
            generated_ids = self.model.generate(pixel_values, max_new_tokens=300) # type: ignore

        decoded_text: list[str] = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

        post_processed_text = [post_process(text) for text in decoded_text]

        return post_processed_text


    

def post_process(text: str):
    spaces_removed: str = "".join(text.split())
    ellipsis_replaced: str = spaces_removed.replace("…", "...")
    periods_replaced: str = re.sub("[・.]{2,}", lambda x: (x.end() - x.start()) * ".", ellipsis_replaced)
    final_text = jaconv.h2z(periods_replaced, ascii=True, digit=True)

    return final_text
