from manga_ocr import MangaOcr
from PIL.Image import Image

#TODO: use multiprocessing?

class OCREngine:
    def __init__(self, device: str) -> None:
        self.device = device
        if self.device == "cpu":
            self.engine = MangaOcr(force_cpu=True)
        else:
            self.engine = MangaOcr(force_cpu=False)

    def get_bubble_text(self, image: Image) -> str:
        return self.engine(image)