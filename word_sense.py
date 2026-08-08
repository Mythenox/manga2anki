import sqlite3
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer, util
from scipy.spatial.distance import cosine
from rhoknp import Morpheme
from create_vocab import Tango
from jamdict import Jamdict
import torch

model = AutoModel.from_pretrained('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

ja_sentence = "嘘ついてませんか"

en_senses = [
    "to breathe out; to breathe",
    "to tell (a lie); to use (foul language)",
    "to vomit; to throw up; to spit up",
]

ja_vec = model.encode(ja_sentence)
en_vecs = model.encode(en_senses)

# Find the closest English sense to the Japanese context
for word, en_vec in zip(en_senses, en_vecs):
    sim = 1 - cosine(ja_vec, en_vec)
    print(f"Similarity to '{word}': {sim:.4f}")

def get_batch_data(words: list[Tango]) -> list[dict]:
    jam = Jamdict()
    batch_data: list[dict] = []
    for word in words:
        result = jam.lookup(word.surface)
        senses = ["; ".join(str(g) for g in sense.gloss) for entry in result.entries for sense in entry.senses]
        word_data: dict = {"text": word.excerpt, "senses": senses}
        batch_data.append(word_data)
    return batch_data
    

def best_word_sense(words: list[Tango]):
    batch_data = get_batch_data(words)

    ja_embeddings = extract_target_vectors_batch(
        [word.morpheme.sentence.morphemes for word in words],
        [word.morpheme.index for word in words],
    )

    unique_senses_dict = {}
    for item in batch_data:
        for sense in item["senses"]:
            if sense not in unique_senses_dict:
                # Map the sense string to an integer index
                unique_senses_dict[sense] = len(unique_senses_dict)

    unique_senses_list = list(unique_senses_dict.keys())

    sense_embeddings = st_model.encode(
        unique_senses_list, 
        batch_size=32, 
        convert_to_tensor=True
    )

    embeddings = model.encode(sentences, batch_size=64, show_progress_bar=True)
    pass

def test_get_candidates(words: list[str]) -> list[str]:
    jam = Jamdict()
    candidates = []
    for word in words:
        result = jam.lookup(word)
        senses = ["; ".join(str(g) for g in sense.gloss) for entry in result.entries for sense in entry.senses]
        candidates.extend(senses)
    return candidates

def extract_target_vectors_batch(
        pre_tokenized_sentences: list[list[Morpheme]],
        target_indices: list[int]
    ) -> :
    """
    pre_tokenized_sentences: List of lists of words e.g., [['川', 'の', ...], ['壁', 'に', ...]]
    target_indices: List of integers representing the target word's index in each sentence
    """
    
    # 1. Tokenize the whole batch at once
    # padding=True ensures all sequences are the same length in the matrix
    inputs = tokenizer(
        pre_tokenized_sentences, 
        is_split_into_words=True, 
        padding=True, 
        truncation=True, 
        return_tensors="pt"
    ).to(device)
    
    # 2. Get the full hidden states for the batch
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Shape: (batch_size, sequence_length, hidden_dimension)
    hidden_states = outputs.last_hidden_state
    batch_size, seq_len, _ = hidden_states.shape
    
    # 3. Create a mask tensor to isolate our target tokens
    # Initialize a mask of zeros matching our batch shape
    mask = torch.zeros((batch_size, seq_len), dtype=torch.float32).to(device)
    
    for i in range(batch_size):
        # word_ids maps the HuggingFace subwords back to the original KNP list indices
        w_ids = inputs.word_ids(batch_index=i)
        for j, w_id in enumerate(w_ids):
            # If this subword belongs to our target KNP index, set mask to 1
            if w_id == target_indices[i]:
                mask[i, j] = 1.0
                
    # Reshape mask from (batch, seq) to (batch, seq, 1) so it multiplies correctly
    mask_expanded = mask.unsqueeze(-1)
    
    # 4. Extract and Average (Vectorized Math)
    # Multiply the hidden states by the mask (turns all non-target vectors to 0)
    target_vectors_sum = (hidden_states * mask_expanded).sum(dim=1)
    
    # Count how many subwords made up each target word
    target_vectors_count = mask_expanded.sum(dim=1)
    
    # Avoid division by zero in case of severe truncation
    target_vectors_count = torch.clamp(target_vectors_count, min=1e-9)
    
    # Average the vectors for each target word
    final_batch_vectors = target_vectors_sum / target_vectors_count
    
    # Returns a tensor of shape (batch_size, hidden_dimension)
    return final_batch_vectors

st_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# If your batch_vectors are on the GPU, ensure this model is too
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
st_model = st_model.to(device)

unique_senses_dict = {}
for item in batch_data:
    for sense in item["senses"]:
        if sense not in unique_senses_dict:
            # Map the sense string to an integer index
            unique_senses_dict[sense] = len(unique_senses_dict)

unique_senses_list = list(unique_senses_dict.keys())

sense_embeddings = st_model.encode(
    unique_senses_list, 
    batch_size=32, 
    convert_to_tensor=True
)