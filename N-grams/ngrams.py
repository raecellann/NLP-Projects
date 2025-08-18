import random
import math
from collections import Counter
from typing import List, Tuple
from text_processor import TextProcessor
from word_analyzer import WordAnalyzer
from phrase_generator import PhraseGenerator


class Ngrams:
    
    def __init__(self, corpus_file: str = "corpus.txt", n: int = 3, num_phrases: int = 5, difficulty: str = "medium"):
        self.corpus_file = corpus_file
        self.n = n
        self.num_phrases = num_phrases
        self.difficulty = difficulty.lower()
        
        self.text_processor = TextProcessor()
        self.word_analyzer = WordAnalyzer()
        self.phrase_generator = PhraseGenerator(n, difficulty)

    def generate_phrases(self) -> List[str]:
        tokens = self.text_processor.get_tokens(self.corpus_file, difficulty_section=self.difficulty)
        return self.phrase_generator.generate_phrases(tokens, self.num_phrases)

    def get_word_frequencies(self, top_k: int = 20) -> List[Tuple[str, int]]:
        tokens = self.text_processor.get_tokens(self.corpus_file, difficulty_section=self.difficulty)
        filtered_tokens = [token for token in tokens 
                          if token not in ["<START>", "<END>"]]
        word_counts = Counter(filtered_tokens)
        return word_counts.most_common(top_k)

    def get_difficulty_stats(self) -> dict:
        tokens = self.text_processor.get_tokens(self.corpus_file, difficulty_section=self.difficulty)
        self.word_analyzer.analyze_word_difficulty(tokens)
        return self.word_analyzer.get_difficulty_stats()

    # Markov fully removed

    def get_model_stats(self) -> dict:
        tokens = self.text_processor.get_tokens(self.corpus_file, difficulty_section=self.difficulty)
        
        filtered_tokens = [token for token in tokens 
                          if token not in ["<START>", "<END>"]]
        
        return {
            "total_tokens": len(tokens),
            "unique_words": len(set(filtered_tokens)),
            "n_gram_order": self.n,
            "vocabulary_size": len(set(filtered_tokens)),
            "difficulty": self.difficulty,
            "difficulty_stats": self.get_difficulty_stats()
        }
    
    def clear_cache(self):
        self.text_processor.clear_cache()
        self.word_analyzer.clear_cache()
        self.phrase_generator.clear_cache()
