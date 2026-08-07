import sqlite3
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

ja_sentence = "嘘ついてませんか"

en_senses = ["to breathe out; to breathe", "to tell (a lie); to use (foul language)​",
              "to vomit; to throw up; to spit up"]

ja_vec = model.encode(ja_sentence)
en_vecs = model.encode(en_senses)

# Find the closest English sense to the Japanese context
for word, en_vec in zip(en_senses, en_vecs):
    sim = 1 - cosine(ja_vec, en_vec)
    print(f"Similarity to '{word}': {sim:.4f}")