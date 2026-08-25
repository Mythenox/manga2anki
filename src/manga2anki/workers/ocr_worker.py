from torch.multiprocessing import Queue
from manga2anki.models.ocr import OCREngine
from cv2.typing import MatLike
from PIL.Image import fromarray
import signal
import logging
from manga2anki.util.logger import configure_worker_logging

# This is currently the bottleneck
# https://huggingface.co/jzhang533/PaddleOCR-VL-For-Manga
# https://huggingface.co/kha-white/manga-ocr-base
# Need to manually redo this worker to do true parallel batching
# Total runtime for ~200 images is about 100s on native Linux

def run_ocr_worker(
        input_queue: Queue,
        output_queue: Queue,
        log_queue: Queue,
        device: str
        ):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    configure_worker_logging(log_queue)
    logging.info(f"Starting OCR worker")
    ocr_engine = OCREngine(device)

    while True:
        bubbles: list[MatLike] | None = input_queue.get()

        if bubbles is None:
            logging.info("OCR worker finished")
            output_queue.put(None)
            break

        for bubble in bubbles:
            pil_bubble = fromarray(bubble)
            text_result: str = ocr_engine.get_bubble_text(pil_bubble)
            output_queue.put(text_result)