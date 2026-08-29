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
from manga2anki.util.constants import KANJI, JA_CHARS
import difflib

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# This is currently the bottleneck
# https://huggingface.co/jzhang533/PaddleOCR-VL-For-Manga
# https://huggingface.co/kha-white/manga-ocr-base
# Need to manually redo this worker to do true parallel batching
# Total runtime for ~200 images is about 100s on native Linux

# great amount fo output where it's literally just dots
# use some kind of hashing and edit distance to reduce duplicates?
# see: locality-sensitive hashing

# weird duplicates/near duplicates issue due to how I'm locating the text bubbles and cropping?
# examine ac_009

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

def run_manga_ocr_worker(
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
    ocr_engine = MangaOcr()

    buffer: deque[Image] = deque()

    while True:
        try:
            item: list[Image] | None = input_queue.get(timeout=timeout_seconds)

            if item is None:
                if len(buffer) > 0:
                    handle_manga_ocr_batch(ocr_engine, buffer, output_queue, output_logger, batch_size)

                logging.info("OCR worker finished")
                output_queue.put(None)
                break

            buffer.extend(item)

            if len(buffer) >= batch_size:
                handle_manga_ocr_batch(ocr_engine, buffer, output_queue, output_logger, batch_size)

        except queue.Empty:
            if len(buffer) > 0:
                handle_manga_ocr_batch(ocr_engine, buffer, output_queue, output_logger, batch_size)

def handle_manga_ocr_batch(
    ocr_engine: MangaOcr,
    buffer: deque,
    output_queue: Queue,
    output_logger: Logger,
    batch_size: int
    ) -> None:
    batch: list[Image] = []
    while buffer:
        while buffer and len(batch) < batch_size:
            batch.append(buffer.popleft())

        bubble_text = []
        for bubble in batch:
            bubble_text.append(ocr_engine(bubble))

        for text in bubble_text:
            output_logger.info(text)
        
        output_queue.put(bubble_text)

        batch = []

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

        """garbage_removed: list[str] = [
            text
            for text in bubble_text
            if not is_garbage(text)
        ]

        deduplicated_text = fuzzy_deduplicate(garbage_removed)"""

        for text in bubble_text:
            output_logger.info(text)

        output_queue.put(bubble_text)

        batch = []

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