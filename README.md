# Manga2Anki
An app that generates an Anki deck from a collection of untranslated manga page scans. Supports filtering by JLPT level,
as well as generating a deck for the purpose of studying kanji instead of vocabulary.

## Motivation
Through my process of learning Japanese, I began to read manga in Japanese to develop my vocabulary.
This can be very grueling, as you often have to look up words that you don't know (which, depending on your choice of manga,
is likely most of them at the beginning) to understand what you're reading. In addition, if you use Anki to try to commit these new words to memory, you have to go back and manually enter the information for each word. From reading the first volume of Spy X Family, for example, I ended up having to manually create almost 200 notes! This app aims to simplify this process by generating the cards for you.

## Quick Start

Clone the repo and run main.py: 

```bash
    python3 src/manga2anki/main.py <input directory or image file>
```

The first time you run the program it might take a few minutes to download
the model weights from HuggingFace.

### Requirements
- rhoknp
- knp

Make sure to install proper codecs to ensure file type support

## Usage

Available flags:
- `-k` or `--kanji-mode` - Outputs an Anki deck for studying kanji instead of vocab
- `-s` or `--strict-filter` - Filters out vocabulary/kanji that do not have a JLPT level
- `-jf` or `--jlpt-floor` - Filters out vocab/kanji with a JLPT level below this number (1-5)
- `-jc` or `--jlpt-ceiling` - Filters out vocab/kanji with a JLPT level above this number (1-5)

## Contributing

Help is very much welcome. Contribute by forking the repo and submitting pull requests to the main branch.
Make sure your code passes the existing tests, and write tests for your changes if applicable.

