from torch.multiprocessing import Queue
from manga2anki.models.ocr import OCREngine
from cv2.typing import MatLike
from PIL.Image import fromarray
import signal
import logging
from manga2anki.util.logger import configure_worker_logging

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
        bubble: MatLike | None = input_queue.get()

        if bubble is None:
            logging.info("OCR worker finished")
            output_queue.put(None)
            break

        pil_bubble = fromarray(bubble)

        text_result: str = ocr_engine.get_bubble_text(pil_bubble)
        output_queue.put(text_result)