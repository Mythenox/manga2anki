"""Process image to text, adding words as cards to an anki deck based on a filter
(default will be N3+ or N4+?). Also add kanji only mode, where it will only add kanji.
Add option to ask for user confirmation, where declined words will be remembered
and ignored in the future. If supplied with a parent deck, words present in the parent
deck will be ignored to avoid redundancy."""

#TODO: use coroutines?

import cv2
from sudachipy import tokenizer
from word import tokenize
from create_vocab import create_vocab
from process_page import get_bubble_text
from genanki import Package
from create_deck import *
# from process_page import get_bubble_text

def main():
    # text = "そもそもどうしてそんな結論になったの？"
    # text = "自分で持続ですか？って聞いてたから大丈夫だと思うけど"
    images = [f"sample/yfnu7-7({i}).png" for i in range(13)]
    text_list: list[str] = get_bubble_text(images)
    
    # text_list = ["そこには、おぞましい光景が広がっていた"]
    tokens = set()
    mode = tokenizer.Tokenizer.SplitMode.C
    for dialogue in text_list:
        dialogue_tokens = tokenize(dialogue, mode)
        tokens.update(dialogue_tokens)
    # tokens = tokenize_text(text)
    deck = create_deck()
    for token in tokens:
        vocab = create_vocab(token, kanji_mode=False)
        if vocab:
            if isinstance(vocab, Tango):
                add_note(deck, vocab)
            else:
                for character in vocab:
                    add_note(deck, character)
    print("Generating .apkg...")
    Package(deck).write_to_file("output.apkg")
    

if __name__ == "__main__":
    main()