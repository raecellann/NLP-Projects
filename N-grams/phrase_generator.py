import random
from typing import List, Optional
from word_analyzer import WordAnalyzer


class PhraseGenerator:
    
    def __init__(self, n: int = 3, difficulty: str = "medium"):
        self.n = n
        self.difficulty = difficulty.lower()
        self.word_analyzer = WordAnalyzer()
        self._difficulty_words_cache: Optional[List[str]] = None
        
        self._difficulty_lengths = {"easy": 6, "medium": 8, "hard": 10}
    
    def generate_phrases(self, tokens: List[str], num_phrases: int) -> List[str]:
        if len(tokens) < max(2, self.n):
            return self._generate_fallback_phrases(tokens, num_phrases)
        
        # Analyze for stats; generation uses wordlist sampling only
        self.word_analyzer.analyze_word_difficulty(tokens)
        
        from collections import Counter
        # Use all words present in the current token set (already filtered by difficulty section)
        alpha_tokens = [t for t in tokens if t not in ("<START>", "<END>") and t.strip() and t.isalpha()]
        word_counts = Counter(alpha_tokens)
        vocabulary = list(dict.fromkeys(alpha_tokens))
        
        def contains_vowel(w: str) -> bool:
            return any(ch in "aeiou" for ch in w.lower())
        
        # Enforce word-length ranges per mode
        def in_length_range(w: str) -> bool:
            L = len(w)
            if self.difficulty == "easy":
                return L <= 4
            if self.difficulty == "medium":
                return 5 <= L <= 7
            return L >= 8
        vocabulary = [w for w in vocabulary if in_length_range(w)]
        
        # Additional quality filters per mode
        if self.difficulty == "easy":
            common_two_letter = {"of","to","in","is","on","by","or","at","an","as","it","be","he","we","me","my","do","go","no","so","up","us"}
            filtered_easy = []
            for w in vocabulary:
                L = len(w)
                if L == 2:
                    if w.lower() in common_two_letter:
                        filtered_easy.append(w)
                    continue
                if L >= 3:
                    if contains_vowel(w) and word_counts[w] >= 2:
                        filtered_easy.append(w)
            # Fallback if too few words after filtering
            if len(filtered_easy) >= max(10, self._get_target_phrase_length()):
                vocabulary = filtered_easy
        else:
            # For medium/hard, at least one vowel to avoid codes/abbreviations (already ensured above)
            # Medium: prefer words with moderate frequency; Hard: prefer rarer/complex words.
            if self.difficulty == "medium":
                filtered_med = [w for w in vocabulary if word_counts[w] >= 2]
                if len(filtered_med) >= max(20, self._get_target_phrase_length()):
                    vocabulary = filtered_med
            elif self.difficulty == "hard":
                filtered_hard = [w for w in vocabulary if word_counts[w] >= 1]
                if len(filtered_hard) >= max(20, self._get_target_phrase_length()):
                    vocabulary = filtered_hard

        # Align with analyzer's difficulty labels as an additional safety net
        try:
            analyzer_words = set(self.word_analyzer.get_words_by_difficulty(self.difficulty))
            vocab_intersection = [w for w in vocabulary if w in analyzer_words]
            # Use intersection if it leaves enough words; else keep previous list
            if len(vocab_intersection) >= max(15, self._get_target_phrase_length()):
                vocabulary = vocab_intersection
        except Exception:
            # Analyzer may not be populated in edge cases; ignore
            pass
        unique_words = list(dict.fromkeys(vocabulary))
        self._difficulty_words_cache = unique_words

        # Always use wordlist sampling with global uniqueness across the generated set
        return self._generate_wordlist_phrases_unique(unique_words, num_phrases)

    def _generate_wordlist_phrases_unique(self, words: List[str], num_phrases: int) -> List[str]:
        phrases: List[str] = []
        used_words = set()
        for _ in range(num_phrases):
            target_len = self._get_target_phrase_length()
            available = [w for w in words if w not in used_words]
            # If enough unused words, sample uniquely
            if len(available) >= target_len:
                sampled = random.sample(available, target_len)
            elif available:
                # Use remaining unused, then fill from all words without immediate duplicates
                sampled = available[:]
                remaining = target_len - len(sampled)
                pool = words
                while remaining > 0 and pool:
                    candidate = random.choice(pool)
                    if sampled and candidate == sampled[-1]:
                        continue
                    sampled.append(candidate)
                    remaining -= 1
            else:
                # All words exhausted; allow reuse but avoid immediate duplicates
                sampled = []
                for _i in range(target_len):
                    candidate = random.choice(words)
                    if sampled and candidate == sampled[-1]:
                        continue
                    sampled.append(candidate)
            # Update used set and finalize
            for w in sampled:
                used_words.add(w)
            phrases.append(" ".join(sampled))
        return phrases
    
    def _generate_single_phrase(self, difficulty_words: List[str]) -> str:
        # No Markov path: use wordlist phrase generation
        words = difficulty_words if difficulty_words else []
        return " ".join(random.sample(words, min(len(words), self._get_target_phrase_length())))
    
    def _detokenize_tokens(self, tokens: List[str]) -> str:
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
    
    def _generate_fallback_phrases(self, tokens: List[str], num_phrases: int) -> List[str]:
        tokens_copy = tokens[:]
        random.shuffle(tokens_copy)
        fallback = " ".join(tokens_copy[:10]) if tokens_copy else ""
        return [fallback for _ in range(num_phrases)]
    
    def _get_target_phrase_length(self) -> int:
        base_length = self._difficulty_lengths.get(self.difficulty, 8)
        return base_length + random.randint(0, 3)
    
    def _generate_token_sequence(self, sequence_tokens: List[str], order: int, 
                                target_len: int, difficulty_words: List[str]) -> List[str]:
        # Markov logic removed; keep signature for compatibility
        return sequence_tokens
    
    def get_difficulty_stats(self) -> dict:
        if not self._difficulty_words_cache:
            raise ValueError("No phrases generated yet. Call generate_phrases() first.")
        
        return self.word_analyzer.get_difficulty_stats()
    
    # Markov fully removed
    
    def clear_cache(self):
        self.word_analyzer.clear_cache()
        self._difficulty_words_cache = None
