from torch.multiprocessing import Queue
import queue
from manga2anki.models.word_sense import WSDEngine, MorphemeDatum
from manga2anki.core.generate_deck import GeneratedDeck
from manga2anki.core.create_cards import batch_create_kanji, batch_create_tango
from rhoknp import KNP
import signal
import logging
from manga2anki.util.logger import configure_worker_logging

# Handle duplicates correctly

def run_wsd_worker(input_queue: Queue, log_queue: Queue, device: str, deck_name: str = "output", batch_size: int = 32, timeout_seconds: float = 2.0):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    configure_worker_logging(log_queue)
    logging.info(f"Starting WSD worker with a batch size of {batch_size}")

    wsd_engine = WSDEngine(device)
    knp = KNP()
    batch_accumulator: list[str] = []
    deck = GeneratedDeck(deck_name)
    unique_morpheme_data: set[MorphemeDatum] = set()

    while True:
        try:
            
            item = input_queue.get(timeout=timeout_seconds)

            if item is None:
                if len(batch_accumulator) > 0:
                    # set of all morphemes in the batch of sentences sitting in batch_accumulator
                    morphemes = [
                        morpheme 
                        for text in batch_accumulator
                        for morpheme in knp.apply_to_sentence(text).morphemes
                    ]
                    final_output = batch_create_tango(morphemes, wsd_engine, unique_morpheme_data)
                    for tango in final_output:
                        deck.add_tango_note(tango)
                    logging.info("Generating .apkg...")
                    deck.package_notes()
                logging.info("WSD worker finished")
                break

            batch_accumulator.append(item)

            if len(batch_accumulator) >= batch_size:
                morphemes = [
                    morpheme 
                    for text in batch_accumulator
                    for morpheme in knp.apply_to_sentence(text).morphemes
                ]
                output = batch_create_tango(morphemes, wsd_engine, unique_morpheme_data)
                for tango in output:
                    deck.add_tango_note(tango)

                # reset queue after processing
                batch_accumulator = []

        except queue.Empty:
            if len(batch_accumulator) > 0:
                logging.info(f"Slow. Only received {len(batch_accumulator)} items in {timeout_seconds:.1f}s.")
                morphemes = [
                    morpheme 
                    for text in batch_accumulator
                    for morpheme in knp.apply_to_sentence(text).morphemes
                ]
                output = batch_create_tango(morphemes, wsd_engine, unique_morpheme_data)
                for tango in output:
                    deck.add_tango_note(tango)

                batch_accumulator = []