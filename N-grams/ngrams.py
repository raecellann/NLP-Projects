import random
import math
from collections import Counter, defaultdict
from typing import List, Tuple, Union, Optional, Sequence
from utils import tokenize


class Ngrams:
    def __init__(self, corpus_file: str = "corpus.txt", n: int = 3, num_phrases: int = 5):
        self.corpus_file = corpus_file
        self.n = n
        self.num_phrases = num_phrases

        self._text_cache: Optional[str] = None
        self._tokens_cache: Optional[List[str]] = None
        self._model_cache: Optional[defaultdict] = None

    def _load_text(self) -> str:
        if self._text_cache is not None:
            return self._text_cache

        try:
            with open(self.corpus_file, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    raise ValueError("Corpus file is empty.")
                self._text_cache = content
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"Corpus file '{self.corpus_file}' not found!")

    def _load_tokens(self) -> List[str]:
        if self._tokens_cache is not None:
            return self._tokens_cache

        text = self._load_text()
        tokens = tokenize(text, special_tokens=True)
        self._tokens_cache = tokens
        return tokens

    def _build_transition_model(self) -> defaultdict:
        if self._model_cache is not None:
            return self._model_cache

        tokens = self._load_tokens()
        order = max(1, self.n - 1)
        model = defaultdict(Counter)
        
        if len(tokens) <= order:
            self._model_cache = model
            return model

        for i in range(len(tokens) - order):
            context = tuple(tokens[i : i + order])
            next_token = tokens[i + order]
            model[context][next_token] += 1
            
        self._model_cache = model
        return model

    def _choose_weighted(self, choices_dict: Counter) -> str:
        tokens = list(choices_dict.keys())
        weights = list(choices_dict.values())
        return random.choices(tokens, weights=weights, k=1)[0]

    def _generate_one_phrase(self, model: defaultdict) -> str:
        order = max(1, self.n - 1)

        start_contexts = [context for context in model.keys() if context[0] == "<START>"]
        if not start_contexts:
            start_contexts = list(model.keys())

        start_context = random.choice(start_contexts)
        sequence_tokens = list(start_context)

        base_by_n = {2: 8, 3: 10, 4: 12}
        target_len = base_by_n.get(self.n, 10) + random.randint(0, 4)

        current_context = start_context
        while len(sequence_tokens) < target_len:
            next_options = model.get(current_context)
            if not next_options:
                break
                
            next_token = self._choose_weighted(next_options)
            sequence_tokens.append(next_token)
            current_context = tuple(sequence_tokens[-order:])
            
            if next_token == "<END>" and len(sequence_tokens) >= order + 4:
                break

        filtered = [t for t in sequence_tokens if t not in ("<START>", "<END>")]
        return self._detokenize(filtered)

    def _detokenize(self, tokens: List[str]) -> str:
        if not tokens:
            return ""
            
        text = ""
        punctuations = {".", ",", "!", "?", ";", ":", "'", '"', ")", "]", "}"}
        no_space_before = punctuations.union({"'", '"'})
        no_space_after = {"(", "[", "{"}

        for i, token in enumerate(tokens):
            if i == 0:
                text += token
                continue
                
            prev_token = tokens[i - 1]

            if token in no_space_before:
                text += token
            elif prev_token in no_space_after:
                text += token
            else:
                text += " " + token
                
        return text

    def generate_phrases(self) -> List[str]:
        tokens = self._load_tokens()
        if len(tokens) < max(2, self.n):
            tokens_copy = tokens[:]
            random.shuffle(tokens_copy)
            fallback = " ".join(tokens_copy[:10]) if tokens_copy else ""
            return [fallback for _ in range(self.num_phrases)]

        model = self._build_transition_model()
        phrases = []
        generated_phrases = set()

        for _ in range(self.num_phrases):
            phrase = ""
            for _ in range(3):
                phrase = self._generate_one_phrase(model)
                if phrase and phrase not in generated_phrases:
                    generated_phrases.add(phrase)
                    phrases.append(phrase)
                    break
            else:
                phrases.append(phrase)

        return phrases

    def suggest_next(
        self, prefix_text: str, top_k: int = 3, use_smoothing: bool = False
    ) -> Sequence[Tuple[str, Union[int, float]]]:
        tokens = self._load_tokens()
        order = max(1, self.n - 1)

        if self.n == 1:
            unigram_counts = Counter(tokens)
            if use_smoothing:
                total = sum(unigram_counts.values())
                vocab_size = max(1, len(unigram_counts))
                probs = [(w, math.log((c + 1) / (total + vocab_size))) 
                         for w, c in unigram_counts.items()]
                probs.sort(key=lambda x: x[1], reverse=True)
                return probs[:top_k]
            return unigram_counts.most_common(top_k)

        model = self._build_transition_model()
        prefix_tokens = tokenize(prefix_text, special_tokens=True)
        context = tuple(prefix_tokens[-order:]) if len(prefix_tokens) >= order else None
        
        if not context or context not in model:
            return []

        next_counter = model[context]
        if use_smoothing:
            total = sum(next_counter.values())
            vocab = set(tokens)
            vocab_size = max(1, len(vocab))
            probabilities = [(w, math.log((count + 1) / (total + vocab_size))) 
                           for w, count in next_counter.items()]
            probabilities.sort(key=lambda x: x[1], reverse=True)
            return probabilities[:top_k]
        else:
            return next_counter.most_common(top_k)

    def get_word_frequencies(self, top_k: int = 20) -> List[Tuple[str, int]]:
        tokens = self._load_tokens()
        filtered_tokens = [token for token in tokens 
                          if token not in ["<START>", "<END>"]]
        word_counts = Counter(filtered_tokens)
        return word_counts.most_common(top_k)

    def get_context_frequencies(self, context: str) -> List[Tuple[str, int]]:
        model = self._build_transition_model()
        order = max(1, self.n - 1)
        
        prefix_tokens = tokenize(context, special_tokens=True)
        context_tuple = tuple(prefix_tokens[-order:]) if len(prefix_tokens) >= order else None
        
        if not context_tuple or context_tuple not in model:
            return []
        
        next_counter = model[context_tuple]
        filtered_items = [(word, freq) for word, freq in next_counter.items() 
                         if word not in ["<START>", "<END>"]]
        filtered_items.sort(key=lambda x: x[1], reverse=True)
        return filtered_items

    def get_model_stats(self) -> dict:
        tokens = self._load_tokens()
        model = self._build_transition_model()
        
        filtered_tokens = [token for token in tokens 
                          if token not in ["<START>", "<END>"]]
        
        return {
            "total_tokens": len(tokens),
            "unique_words": len(set(filtered_tokens)),
            "n_gram_order": self.n,
            "contexts": len(model),
            "vocabulary_size": len(set(filtered_tokens)),
            "most_common_words": self.get_word_frequencies(5)
        }
