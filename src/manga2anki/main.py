"""Process image to text, adding words as cards to an anki deck based on a filter
(default will be N3+ or N4+?). Also add kanji only mode, where it will only add kanji.
Add option to ask for user confirmation, where declined words will be remembered
and ignored in the future. If supplied with a parent deck, words present in the parent
deck will be ignored to avoid redundancy."""

from manga2anki.util.process_page import get_bubble_text
from genanki import Package
from manga2anki.core.generate_deck import GeneratedDeck
from rhoknp import KNP
from manga2anki.core.batch_create import batch_create_tango, batch_create_kanji

def main():
    knp = KNP()
    # text = "そもそもどうしてそんな結論になったの？"
    # text = "自分で持続ですか？って聞いてたから大丈夫だと思うけど"
    images = [f"sample/yfnu7-7({i}).png" for i in range(13)]
    text_list: list[str] = get_bubble_text(images)

    all_morphemes = []
    for dialogue in text_list:
        sentence = knp.apply_to_sentence(dialogue)
        all_morphemes.extend(sentence.morphemes)
    
    # text_list = ["そこには、おぞましい光景が広がっていた"]
    # tokens = tokenize_text(text)
    generated_deck = GeneratedDeck()
    kanji_list = batch_create_kanji(all_morphemes)
    for kanji in kanji_list:
        generated_deck.add_kanji_note(kanji)
    print("Generating .apkg...")
    Package(generated_deck.deck).write_to_file("output.apkg")
    

if __name__ == "__main__":
    main()