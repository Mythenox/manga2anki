import asyncio
from manga2anki.core.vocab import Tango, Kanji
from genanki import Deck, Note
from manga2anki.core.generate_deck import GeneratedDeck

class AsyncVocabProcessor:
    def __init__(self, max_concurrency, words: list[Word]) -> None:
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.deck: Deck = create_deck()
        self.session = None
        self.words = words
        self.vocab_list: list[Tango | Kanji] = []


    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def get_html(self, vocab: Tango | Kanji):
        pass

    async def fetch_tango_html(self, vocab: Tango | Kanji):
        pass


    async def process_vocab(self):
        tasks = []
        for word in self.words:
            vocab = create_vocab(word)
            if isinstance(vocab, Tango):
                vocab_html = await self.get_html(vocab) 
            elif vocab is not None: # i.e. is of type list[Kanji]
                pass
                

