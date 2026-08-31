from torch.multiprocessing import Queue
from manga2anki.models.ocr import OCREngine
from cv2.typing import MatLike
from PIL.Image import Image
import signal
import logging
from logging import Logger
from transformers.utils import logging as hf_logging
from manga2anki.util.logger import configure_worker_logging
import queue
from collections import deque
from manga_ocr import MangaOcr

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# This is currently the bottleneck
# https://huggingface.co/jzhang533/PaddleOCR-VL-For-Manga
# https://huggingface.co/kha-white/manga-ocr-base
# Need to manually redo this worker to do true parallel batching
# Total runtime for ~200 images is about 100s on native Linux

# fixed: great amount fo output where it's literally just dots
# use some kind of hashing and edit distance to reduce duplicates?
# see: locality-sensitive hashing

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

    output_logger = logging.getLogger("ocr_output")
    output_logger.setLevel(logging.INFO)
    output_logger.propagate = False
    file_handler = logging.FileHandler("ocr_output.log", mode="w")
    formatter = logging.Formatter("%(message)s")
    file_handler.setFormatter(formatter)
    output_logger.addHandler(file_handler)

    logging.info(f"Starting OCR worker")
    ocr_engine = OCREngine(device)

    buffer: deque[Image] = deque()

    while True:
        try:
            item: list[Image] | None = input_queue.get(timeout=timeout_seconds)

            if item is None:
                if len(buffer) > 0:
                    handle_batch(ocr_engine, buffer, output_queue, output_logger, batch_size)

                logging.info("OCR worker finished")
                output_queue.put(None)
                break

            buffer.extend(item)

            if len(buffer) >= batch_size:
                handle_batch(ocr_engine, buffer, output_queue, output_logger, batch_size)

        except queue.Empty:
            if len(buffer) > 0:
                handle_batch(ocr_engine, buffer, output_queue, output_logger, batch_size)

def handle_batch(
    ocr_engine: OCREngine,
    buffer: deque,
    output_queue: Queue,
    output_logger: Logger,
    batch_size: int
    ) -> None:
    batch: list[Image] = []
    while buffer:
        while buffer and len(batch) < batch_size:
            batch.append(buffer.popleft())

        bubble_text: list[str] = ocr_engine.get_bubble_text(batch)

        for text in bubble_text:
            output_logger.info(text)

        output_queue.put(bubble_text)

        batch = []