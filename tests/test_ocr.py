import time
import torch.multiprocessing as mp
from manga2anki.workers.cv_worker import run_cv_worker
from manga2anki.workers.ocr_worker import run_ocr_worker
from manga2anki.workers.wsd_worker import run_wsd_worker, dummy_consumer
from manga2anki.util.get_images import get_all_images
import sys
import numpy as np
from manga2anki.util.logger import start_logger_listener, configure_worker_logging
import logging

def main():
    start_time = time.perf_counter()
    mp.set_start_method("spawn")
    device = "cuda"

    log_queue = mp.Queue()
    log_listener = start_logger_listener(log_queue)

    configure_worker_logging(log_queue)

    cv_to_ocr_queue = mp.Queue()
    ocr_to_wsd_queue = mp.Queue()

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
    dummy_proc = mp.Process(target=dummy_consumer, args=(ocr_to_wsd_queue,))
    ocr_proc.start()
    dummy_proc.start()

    all_processes = cv_processes + [ocr_proc, dummy_proc]

    try:
        for p in cv_processes:
            p.join()

        cv_to_ocr_queue.put(None)

        ocr_proc.join()
        dummy_proc.join()

        duration = time.perf_counter() - start_time
        logging.info(f"Finished in {duration:.2f} seconds")
        log_listener.stop()
    except KeyboardInterrupt:
        for p in all_processes:
            if p.is_alive():
                p.terminate()
                p.join()

        sys.exit(1)
    

if __name__ == "__main__":
    main()