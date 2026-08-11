from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer, util
from rhoknp import Morpheme
from jamdict import Jamdict
import torch
from typing import TypedDict
from manga2anki.util.inflect import lemmatize_surface, lemmatize_reading
from dataclasses import dataclass

@dataclass
class MorphemeDatum:
    morpheme: Morpheme
    jlpt_level: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MorphemeDatum):
            return False
        return (
            lemmatize_surface(self.morpheme) == lemmatize_surface(other.morpheme) and
            lemmatize_reading(self.morpheme) == lemmatize_reading(other.morpheme) and
            self.morpheme.pos == other.morpheme.pos and
            self.jlpt_level == other.jlpt_level
        )

    def __hash__(self) -> int:
        return hash((
            lemmatize_surface(self.morpheme),
            lemmatize_reading(self.morpheme),
            self.morpheme.pos,
            self.jlpt_level,
        ))

class SenseDatum(TypedDict):
    morpheme_datum: MorphemeDatum
    senses: list[str]

class SenseResult(TypedDict):
    morpheme_datum: MorphemeDatum
    best_sense: str

class WSDEngine:
    def __init__(
            self,
            device: str,
            model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ) -> None:
        if device == "cuda" and torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif device == "mps" and torch.backends.mps.is_available():
            self.device = torch.device("mds")
        else:
            if device != "cpu":
                print("Given device not available, falling back to CPU")
            self.device = torch.device("cpu")

        self.ja_model = AutoModel.from_pretrained(model_name).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.st_model = SentenceTransformer(model_name).to(self.device)

    def predict_word_sense(
        self,
        morpheme_data: list[MorphemeDatum],
    ) -> list[SenseResult]:

        morphemes = [item.morpheme for item in morpheme_data]

        batch_data = get_batch_data(morpheme_data)

        ja_embeddings = self.extract_target_vectors_batch(
            [[m.surf for m in morpheme.sentence.morphemes] for morpheme in morphemes],
            [morpheme.index for morpheme in morphemes],
        )

        unique_senses_dict = {}
        for item in batch_data:
            for sense in item["senses"]:
                if sense not in unique_senses_dict:
                    # Map the sense string to an integer index
                    unique_senses_dict[sense] = len(unique_senses_dict)

        unique_senses_list = list(unique_senses_dict.keys())

        sense_embeddings = self.st_model.encode(
            unique_senses_list, 
            batch_size=32, 
            convert_to_tensor=True
        )

        results: list[SenseResult] = []

        # Loop through the batch items to map the correct vectors together
        for i, item in enumerate(batch_data):

            if not item["senses"]:
                results.append({
                    "morpheme_datum": item["morpheme_datum"],
                    "best_sense": ""
                })
                continue
            
            target_vec = ja_embeddings[i]
            sense_indices = [unique_senses_dict[s] for s in item["senses"]]
            candidate_vecs = sense_embeddings[sense_indices]
            
            similarities = util.cos_sim(target_vec, candidate_vecs)[0]
            
            best_idx = int(torch.argmax(similarities).item())
            best_sense = item["senses"][best_idx]
            best_score = similarities[best_idx].item()
            
            results.append({
                "morpheme_datum": item["morpheme_datum"],
                "best_sense": best_sense,
            })

        return results

    def extract_target_vectors_batch(
        self,
        pre_tokenized_sentences: list[list[str]],
        target_indices: list[int],
    ):
        """
        pre_tokenized_sentences: List of lists of words e.g., [['川', 'の', ...], ['壁', 'に', ...]]
        target_indices: List of integers representing the target word's index in each sentence
        """
        
        inputs = self.tokenizer(
            pre_tokenized_sentences, 
            is_split_into_words=True, 
            padding=True, 
            truncation=True, 
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.ja_model(**inputs)
        
        hidden_states = outputs.last_hidden_state

        mask_list = []
        for i, target_idx in enumerate(target_indices):
            w_ids = inputs.word_ids(batch_index=i)
            # w_ids contains None for special tokens (like [CLS], [SEP], padding)
            # We build the row using a fast list comprehension
            row = [1.0 if w == target_idx else 0.0 for w in w_ids]
            mask_list.append(row)

        mask = torch.tensor(mask_list, dtype=torch.float32, device=self.device)
        
        for i, target_idx in enumerate(target_indices):
            w_ids = inputs.word_ids(batch_index=i)
            for j, w_id in enumerate(w_ids):
                if w_id == target_idx:
                    mask[i, j] = 1.0

        mask_expanded = mask.unsqueeze(-1)
        target_vectors_sum = (hidden_states * mask_expanded).sum(dim=1)

        target_vectors_count = mask_expanded.sum(dim=1)
        target_vectors_count = torch.clamp(target_vectors_count, min=1e-9)
        
        final_batch_vectors = target_vectors_sum / target_vectors_count
        
        return final_batch_vectors

def get_batch_data(morpheme_data: list[MorphemeDatum]) -> list[SenseDatum]:
    """"
    Dict shape:
    {
        "morpheme": morpheme,
        "senses": list of senses corresponding to morpheme
    }
    """
    jam = Jamdict()
    batch_data: list[SenseDatum] = []
    for morpheme_datum in morpheme_data:
        result = jam.lookup(lemmatize_surface(morpheme_datum.morpheme))
        senses = ["; ".join(str(g) for g in sense.gloss) for entry in result.entries for sense in entry.senses]
        sense_datum: SenseDatum = {"morpheme_datum": morpheme_datum, "senses": senses}
        batch_data.append(sense_datum)
    return batch_data



def test_get_candidates(words: list[str]) -> list[str]:
    jam = Jamdict()
    candidates = []
    for word in words:
        result = jam.lookup(word)
        senses = ["; ".join(str(g) for g in sense.gloss) for entry in result.entries for sense in entry.senses]
        candidates.extend(senses)
    return candidates
