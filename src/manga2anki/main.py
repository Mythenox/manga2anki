"""Process image to text, adding words as cards to an anki deck based on a filter
(default will be N3+ or N4+?). Also add kanji only mode, where it will only add kanji.
Add option to ask for user confirmation, where declined words will be remembered
and ignored in the future. If supplied with a parent deck, words present in the parent
deck will be ignored to avoid redundancy."""

# TODO: add support for epub and mobi file types?
# TODO: add support for only allowing JLPT vocab/kanji
# TODO: add strict flag to not add vocab that do not have a jmdict definition
# TODO: add  wanikani levels as well

import time
import torch.multiprocessing as mp
from manga2anki.workers.cv_worker import run_cv_worker
from manga2anki.workers.ocr_worker import run_ocr_worker
from manga2anki.workers.wsd_worker import run_wsd_worker
from manga2anki.util.get_images import get_all_images
import sys
import numpy as np
from manga2anki.util.logger import start_logger_listener
import logging

def main():
    start_time = time.perf_counter()
    mp.set_start_method("spawn")
    device = "cuda"

    log_queue = mp.Queue()
    log_listener = start_logger_listener(log_queue)

    cv_to_ocr_queue = mp.Queue(maxsize=100)
    ocr_to_wsd_queue = mp.Queue(maxsize=100)

    path_str = "sample/yfnu7-full/"

    image_paths = get_all_images(path_str)
    if len(image_paths) == 0:
        print("Either the provided file or directory does not exist, or no valid file types were found")
        sys.exit(1)

    num_cv_workers = 4
    chunks = np.array_split(image_paths, num_cv_workers)

    logging.info("Starting pipeline...")

    cv_processes = []

    for chunk in chunks:
        p = mp.Process(target=run_cv_worker, args=(chunk.tolist(), cv_to_ocr_queue, log_queue))
        p.start()
        cv_processes.append(p)

    ocr_proc = mp.Process(target=run_ocr_worker, args=(cv_to_ocr_queue, ocr_to_wsd_queue, log_queue, device))
    wsd_proc = mp.Process(target=run_wsd_worker, args=(ocr_to_wsd_queue, log_queue, device))

    ocr_proc.start()
    wsd_proc.start()

    all_processes = cv_processes + [ocr_proc, wsd_proc]

    try:
        for p in cv_processes:
            p.join()

        cv_to_ocr_queue.put(None)

        ocr_proc.join()
        wsd_proc.join()

        logging.info("Pipeline complete")
        log_listener.stop()

        duration = time.perf_counter() - start_time
        print(f"Computed in {duration} seconds")
    except KeyboardInterrupt:
        for p in all_processes:
            if p.is_alive():
                p.terminate()
                p.join()

        sys.exit(1)
    

if __name__ == "__main__":
    main()