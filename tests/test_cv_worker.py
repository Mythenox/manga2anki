import logging
import time
from manga2anki.util.logger import configure_worker_logging
import torch.multiprocessing as mp
from torch.multiprocessing import Queue
import cv2
from cv2.typing import MatLike
from manga2anki.core.speech_bubble import preprocess, resize_crops
import signal
from manga2anki.util.logger import start_logger_listener
from manga2anki.util.get_images import get_all_images
import sys
import numpy as np

def main():
    start_time = time.perf_counter()
    mp.set_start_method("spawn")
    log_queue = mp.Queue()
    log_listener = start_logger_listener(log_queue)

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
        p = mp.Process(target=run_cv_worker, args=(chunk.tolist(), log_queue))
        p.start()
        cv_processes.append(p)

    try:
        for p in cv_processes:
            p.join()

        logging.info("Pipeline complete")
        log_listener.stop()

        duration = time.perf_counter() - start_time
        print(f"Computed in {duration} seconds")
    except KeyboardInterrupt:
        for p in cv_processes:
            if p.is_alive():
                p.terminate()
                p.join()

        sys.exit(1)

def run_cv_worker(
        image_paths_chunk: list[str],
        log_queue: Queue
        ):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    configure_worker_logging(log_queue)
    logging.info(f"Starting OpenCV worker for {len(image_paths_chunk)} images")

    total_preprocess_time = 0.0
    total_contour_time = 0.0
    total_resize_time = 0.0

    for path in image_paths_chunk:
        img = cv2.imread(path)
        if img is None:
            continue

        t0 = time.time()
        # t0
        prepped_image = preprocess(img, True)
        # t1
        t1 = time.time()

        total_preprocess_time += (t1 - t0)

        # t2
        t2 = time.time()
        contours = cv2.findContours(
            prepped_image,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE,
        )[0]
        # t3
        t3 = time.time()

        total_contour_time += (t3 - t2)

        cropped_images: list[MatLike] = []
        cropped_image_dims: list[tuple[int, int, int, int]] = []
    
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
    
            # filter out speech bubbles with unreasonable size
            if (60 < w < 400) and (25 < h < 500):
                cropped_images.append(img[y:y+h, x:x+w])
                cropped_image_dims.append((x, y, x+w, y+h))

        # t4
        t4 = time.time()
        resized_crops = resize_crops(cropped_images)
        # t5
        t5 = time.time()

        total_resize_time += (t5 - t4)

        bubbles = resized_crops

    logging.info(f"""OpenCV worker finished. Preprocess time: {total_preprocess_time:.2f}s
| Contour time: {total_contour_time:.2f}s | Resize time: {total_resize_time:.2f}s""")


if __name__ == "__main__":
    main()