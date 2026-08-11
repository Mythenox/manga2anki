import logging
import logging.handlers
import sys

def start_logger_listener(log_queue, log_file="pipeline.log"):
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '%(asctime)s | %(processName)-18s | %(levelname)-7s | %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    listener = logging.handlers.QueueListener(
        log_queue, file_handler, console_handler
    )
    listener.start()

    return listener

def configure_worker_logging(log_queue):
    queue_handler = logging.handlers.QueueHandler(log_queue)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    root_logger.handlers = []
    root_logger.addHandler(queue_handler)