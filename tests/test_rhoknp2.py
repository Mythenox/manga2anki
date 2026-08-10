from rhoknp import Jumanpp, KNP

knp = KNP()
text = "綺麗な水が静かに垂れている"

sentence = knp.apply_to_sentence(text)

"""print("========== Clauses ==========")
for clause in sentence.clauses:  # a.k.a., setsu
    print(clause)

print("========== Phrases ==========")
for phrase in sentence.phrases:  # a.k.a. bunsetsu
    print(phrase)

print("========== Base Phrases ==========") 
for base_phrase in sentence.base_phrases:  # a.k.a. kihon-ku
    print(base_phrase)

print("========== Morphemes ==========")
for morpheme in sentence.morphemes:
    print(morpheme)"""

for morpheme in sentence.morphemes:
    print(f"{morpheme}: {morpheme.lemma}, {morpheme.reading}")
    canon = morpheme.semantics.get("代表表記")
    if canon:
        print(morpheme.semantics.get("代表表記"))