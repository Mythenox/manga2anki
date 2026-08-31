from torch.multiprocessing import Queue
import queue
from manga2anki.models.word_sense import WSDEngine, MorphemeDatum
from manga2anki.core.generate_deck import GeneratedDeck
from manga2anki.core.create_cards import batch_create_kanji, batch_create_tango
from rhoknp import Jumanpp
import signal
import logging
from logging import Logger
from manga2anki.util.logger import configure_worker_logging
from collections import deque
from manga2anki.core.create_cards import Morpheme

# Seriously need to figure out how to turn off the logging progress bars

# grab list, create morphemes, batch process morphemes $batch_size at a time

def run_wsd_worker(
        input_queue: Queue, log_queue: Queue,
        device: str, 
        deck_name: str = "output",
        batch_size: int = 32, 
        timeout_seconds: float = 2.0
        ):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    configure_worker_logging(log_queue)
    logging.info(f"Starting WSD worker with a batch size of {batch_size}")

    wsd_engine = WSDEngine(device)
    jpp = Jumanpp()
    batch_accumulator: list[str] = []
    deck = GeneratedDeck(deck_name)
    unique_morpheme_data: set[MorphemeDatum] = set()

    buffer: deque[Morpheme] = deque()

    while True:
        try:
            
            item: list[str] | None = input_queue.get(timeout=timeout_seconds)

            if item is None:
                if len(buffer) > 0:
                    handle_batch(wsd_engine, buffer, unique_morpheme_data, deck, batch_size)
                    logging.info("Generating .apkg...")
                    deck.package_notes()
                logging.info("WSD worker finished")
                break

            morphemes = [
                morpheme 
                for text in batch_accumulator
                for morpheme in jpp.apply_to_sentence(text).morphemes
            ]

            buffer.extend(morphemes)

            if len(buffer) >= batch_size:
                handle_batch(wsd_engine, buffer, unique_morpheme_data, deck, batch_size)

        except queue.Empty:
            if len(buffer) > 0:
                logging.info(f"Slow. Only received {len(batch_accumulator)} items in {timeout_seconds:.1f}s.")
                handle_batch(wsd_engine, buffer, unique_morpheme_data, deck, batch_size)

def handle_batch(
    wsd_engine: WSDEngine,
    buffer: deque,
    unique_morpheme_data: set[MorphemeDatum],
    deck: GeneratedDeck,
    batch_size: int,
    ) -> None:
    batch: list[Morpheme] = []
    while buffer:
        while buffer and len(batch) < batch_size:
            batch.append(buffer.popleft())

        output = batch_create_tango(batch, wsd_engine, unique_morpheme_data)
        for tango in output:
            deck.add_tango_note(tango)

        batch = []


def dummy_consumer(q: Queue):
    while True:
        item = q.get()
        if item is None:
            break
    