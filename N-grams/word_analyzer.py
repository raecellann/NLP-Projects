from collections import Counter
from typing import Dict, List


class WordAnalyzer:
    
    def __init__(self):
        self._word_difficulty_cache: Dict[str, str] = {}
        self._tokens_analyzed: List[str] = []
    
    def analyze_word_difficulty(self, tokens: List[str]) -> Dict[str, str]:
        if self._word_difficulty_cache and self._tokens_analyzed == tokens:
            return self._word_difficulty_cache

        filtered_tokens = [token for token in tokens 
                          if token not in ["<START>", "<END>"] and len(token) > 1]
        
        word_counts = Counter(filtered_tokens)
        word_scores = self._calculate_word_complexity_scores(word_counts)
        word_difficulty = self._categorize_words_by_difficulty(word_scores)
        
        self._word_difficulty_cache = word_difficulty
        self._tokens_analyzed = tokens[:]
        return word_difficulty
    
    def _calculate_word_complexity_scores(self, word_counts: Counter) -> dict:
        word_scores = {}
        
        for word, count in word_counts.items():
            if len(word) < 2:
                continue
                
            length_score = self._calculate_length_score(word)
            freq_score = self._calculate_frequency_score(word, count, word_counts)
            complexity_score = self._calculate_pattern_complexity_score(word)
            syllable_score = self._calculate_syllable_score(word)
            
            total_score = length_score + freq_score + complexity_score + syllable_score
            word_scores[word] = total_score
        
        return word_scores
    
    def _calculate_length_score(self, word: str) -> float:
        return len(word) * 0.3
    
    def _calculate_frequency_score(self, word: str, count: int, word_counts: Counter) -> float:
        total_words = sum(word_counts.values())
        return (1 - (count / total_words)) * 5
    
    def _calculate_pattern_complexity_score(self, word: str) -> float:
        complexity_score = 0.0
        consonants = 0
        
        for char in word.lower():
            if char in 'aeiou':
                consonants = 0
            elif char.isalpha():
                consonants += 1
                if consonants >= 3:
                    complexity_score += 1.0
            else:
                complexity_score += 0.5
        
        return complexity_score
    
    def _calculate_syllable_score(self, word: str) -> float:
        consonants = sum(1 for char in word.lower() if char.isalpha() and char not in 'aeiou')
        vowels = sum(1 for char in word.lower() if char in 'aeiou')
        
        syllable_count = max(1, (consonants + vowels) // 3)
        return syllable_count * 0.5
    
    def _categorize_words_by_difficulty(self, word_scores: dict) -> dict:
        sorted_words = sorted(word_scores.items(), key=lambda x: x[1])
        total_words = len(sorted_words)
        
        easy_threshold = int(total_words * 0.4)
        medium_threshold = int(total_words * 0.8)
        
        word_difficulty = {}
        for i, (word, score) in enumerate(sorted_words):
            if i < easy_threshold:
                word_difficulty[word] = "easy"
            elif i < medium_threshold:
                word_difficulty[word] = "medium"
            else:
                word_difficulty[word] = "hard"
        
        return word_difficulty

    def get_words_by_difficulty(self, difficulty: str) -> List[str]:
        if not self._word_difficulty_cache:
            raise ValueError("No word difficulty analysis performed yet. Call analyze_word_difficulty() first.")
        
        return [word for word, diff in self._word_difficulty_cache.items() if diff == difficulty]
    
    def get_difficulty_stats(self) -> Dict[str, Dict]:
        if not self._word_difficulty_cache:
            raise ValueError("No word difficulty analysis performed yet. Call analyze_word_difficulty() first.")
        
        easy_words = [word for word, diff in self._word_difficulty_cache.items() if diff == "easy"]
        medium_words = [word for word, diff in self._word_difficulty_cache.items() if diff == "medium"]
        hard_words = [word for word, diff in self._word_difficulty_cache.items() if diff == "hard"]
        
        return {
            "easy": {
                "count": len(easy_words),
                "sample_words": easy_words[:10]
            },
            "medium": {
                "count": len(medium_words),
                "sample_words": medium_words[:10]
            },
            "hard": {
                "count": len(hard_words),
                "sample_words": hard_words[:10]
            }
        }
    
    def clear_cache(self):
        self._word_difficulty_cache.clear()
        self._tokens_analyzed.clear()
