from torch.multiprocessing import Queue
from manga2anki.models.ocr import OCREngine
from cv2.typing import MatLike
from PIL.Image import fromarray
import signal
import logging
from manga2anki.util.logger import configure_worker_logging
from manga2anki.workers.cv_worker import TaggedBubble

# This is currently the bottleneck
# https://huggingface.co/jzhang533/PaddleOCR-VL-For-Manga
# https://huggingface.co/kha-white/manga-ocr-base
# Need to manually redo this worker to do true parallel batching
# Total runtime for ~200 images is about 100s on native Linux

def run_ocr_worker(
        input_queue: Queue,
        output_queue: Queue,
        log_queue: Queue,
        device: str,
        batch_size: int = 32, 
        timeout_seconds: float = 2.0
        ):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    configure_worker_logging(log_queue)
    logging.info(f"Starting OCR worker")
    ocr_engine = OCREngine(device)
    batch_accumulator: list[TaggedBubble] = []

    while True:
        try:
            item: list[TaggedBubble] = input_queue.get(timeout=timeout_seconds)

            if item is None:
                if len(batch_accumulator) > 0:
                    text_result: list[str] = ocr_engine.get_bubble_text(batch_accumulator)
                    output_queue.put(text_result)
                logging.info("OCR worker finished")
                output_queue.put(None)
                break

            batch_accumulator.extend(item)

            if len(batch_accumulator) >= batch_size:
                text_result: list[str] = ocr_engine.get_bubble_text(batch_accumulator)
                output_queue.put(text_result)

                batch_accumulator = []

            


    while True:
        tagged_bubbles: list[TaggedBubble] = input_queue.get()

        if tagged_bubbles is None:
            logging.info("OCR worker finished")
            output_queue.put(None)
            break

        text_result: list[str] = ocr_engine.get_bubble_text(pil_bubble)
        output_queue.put(text_result)