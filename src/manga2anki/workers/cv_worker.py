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

# This is currently the bottleneck

def run_cv_worker(image_paths_chunk: list[str], output_queue: Queue, log_queue: Queue):
    # cv2.setNumThreads(1)
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    configure_worker_logging(log_queue)
    logging.info(f"Starting OpenCV worker for {len(image_paths_chunk)} images")

    total_io_time = 0.0
    total_compute_time = 0.0

    for path in image_paths_chunk:
        t0 = time.time()
        img = cv2.imread(path)
        t1 = time.time()
        if img is None:
            continue
        total_io_time += (t1 - t0)

        t2 = time.time()
        
        bubbles = get_bubbles(img)
        for bubble in bubbles:
            output_queue.put(bubble)
        t3 = time.time()
        total_compute_time += (t3 - t2)

    logging.info(f"OpenCV worker finished. I/O Time: {total_io_time:.2f}s | Compute Time: {total_compute_time:.2f}s")