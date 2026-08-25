from rhoknp import Jumanpp

jumanpp = Jumanpp()

morphemes = jumanpp.apply_to_sentence("おいおい政治されてるぞ！").morphemes

for morpheme in morphemes:
    print(morpheme)