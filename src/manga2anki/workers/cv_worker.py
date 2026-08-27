from manga2anki.core.speech_bubble import get_bubbles
import os
import sys
import cv2
from cv2.typing import MatLike
from torch.multiprocessing import Queue
import signal
from manga2anki.util.logger import configure_worker_logging
import logging
import time
from typing import TypedDict

class TaggedBubble(TypedDict):
    id: str
    img: MatLike

def run_cv_worker(
        image_paths_chunk: list[str],
        output_queue: Queue,
        log_queue: Queue,
        worker_id: int
        ):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    configure_worker_logging(log_queue)
    logging.info(f"Starting OpenCV worker for {len(image_paths_chunk)} images")

    total_io_time = 0.0
    total_compute_time = 0.0
    total_queue_time = 0.0

    for path in image_paths_chunk:
        t0 = time.time()
        img = cv2.imread(path)
        t1 = time.time()
        if img is None:
            continue
        total_io_time += (t1 - t0)

        t2 = time.time()
        
        bubbles: list[MatLike] = get_bubbles(img)
        t3 = time.time()
        total_compute_time += (t3 - t2)

        t4 = time.time()
        tagged_bubbles: list[TaggedBubble] = [{"id": f"w{worker_id}i{i}", "img": bubble} for i, bubble in enumerate(bubbles)]
        output_queue.put(tagged_bubbles)
        t5 = time.time()
        total_queue_time += (t5 - t4)
        

    logging_result = (
        f"OpenCV worker finished. I/O Time: {total_io_time:.2f}s "
        f"| Compute Time: {total_compute_time:.2f}s "
        f"| Queue Time: {total_queue_time:.2f}s"
    )

    logging.info(logging_result)