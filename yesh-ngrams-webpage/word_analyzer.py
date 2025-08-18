from collections import Counter
from typing import Dict, List


class WordAnalyzer:

	def __init__(self):
		self._word_difficulty_cache: Dict[str, str] = {}
		self._tokens_analyzed: List[str] = []

	def analyze_word_difficulty(self, tokens: List[str]) -> Dict[str, str]:
		if self._word_difficulty_cache and self._tokens_analyzed == tokens:
			return self._word_difficulty_cache
		filtered_tokens = [t for t in tokens if t not in ("<START>", "<END>") and len(t) > 1]
		counts = Counter(filtered_tokens)
		scores = self._calculate_word_complexity_scores(counts)
		mapping = self._categorize_words_by_difficulty(scores)
		self._word_difficulty_cache = mapping
		self._tokens_analyzed = tokens[:]
		return mapping

	def _calculate_word_complexity_scores(self, word_counts: Counter) -> dict:
		word_scores = {}
		for word, count in word_counts.items():
			if len(word) < 2:
				continue
			length_score = len(word) * 0.3
			total_words = sum(word_counts.values())
			freq_score = (1 - (count / total_words)) * 5
			complexity_score = 0.0
			consecutive_consonants = 0
			for ch in word.lower():
				if ch in 'aeiou':
					consecutive_consonants = 0
				elif ch.isalpha():
					consecutive_consonants += 1
					if consecutive_consonants >= 3:
						complexity_score += 1.0
				else:
					complexity_score += 0.5
			vowels = sum(1 for ch in word.lower() if ch in 'aeiou')
			consonants = sum(1 for ch in word.lower() if ch.isalpha() and ch not in 'aeiou')
			syllable_count = max(1, (vowels + consonants) // 3)
			syllable_score = syllable_count * 0.5
			total = length_score + freq_score + complexity_score + syllable_score
			word_scores[word] = total
		return word_scores

	def _categorize_words_by_difficulty(self, word_scores: dict) -> dict:
		sorted_words = sorted(word_scores.items(), key=lambda x: x[1])
		n = len(sorted_words)
		easy_th = int(n * 0.4)
		med_th = int(n * 0.8)
		mapping: Dict[str, str] = {}
		for i, (w, _) in enumerate(sorted_words):
			if i < easy_th:
				mapping[w] = 'easy'
			elif i < med_th:
				mapping[w] = 'medium'
			else:
				mapping[w] = 'hard'
		return mapping

	def get_words_by_difficulty(self, difficulty: str) -> List[str]:
		if not self._word_difficulty_cache:
			raise ValueError('Call analyze_word_difficulty() first')
		return [w for w, d in self._word_difficulty_cache.items() if d == difficulty]

	def get_difficulty_stats(self) -> Dict[str, Dict]:
		if not self._word_difficulty_cache:
			raise ValueError('Call analyze_word_difficulty() first')
		easy = [w for w, d in self._word_difficulty_cache.items() if d == 'easy']
		med = [w for w, d in self._word_difficulty_cache.items() if d == 'medium']
		hard = [w for w, d in self._word_difficulty_cache.items() if d == 'hard']
		return {
			'easy': {'count': len(easy), 'sample_words': easy[:10]},
			'medium': {'count': len(med), 'sample_words': med[:10]},
			'hard': {'count': len(hard), 'sample_words': hard[:10]},
		}

	def clear_cache(self):
		self._word_difficulty_cache.clear()
		self._tokens_analyzed.clear()


