import torch
from transformers import AutoImageProcessor, AutoTokenizer, VisionEncoderDecoderModel
from PIL.Image import Image
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
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name).to(self.device).half() # type: ignore

        
    """Returns a list of sentences/excerpts, each coming from a different speech bubble."""
    def get_bubble_text(self, bubbles: list[Image]) -> list[str]:
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

        return post_processed_text


def post_process(text: str):
    spaces_removed: str = "".join(text.split())
    ellipsis_replaced: str = spaces_removed.replace("…", "...")
    periods_replaced: str = re.sub("[・.]{2,}", lambda x: (x.end() - x.start()) * ".", ellipsis_replaced)
    final_text = jaconv.h2z(periods_replaced, ascii=True, digit=True)

    return final_text
