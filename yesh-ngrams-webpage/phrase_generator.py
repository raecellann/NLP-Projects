import random
from typing import List
from word_analyzer import WordAnalyzer


class PhraseGenerator:

	def __init__(self, n: int = 3, difficulty: str = 'medium'):
		self.n = n
		self.difficulty = (difficulty or 'medium').lower()
		self.word_analyzer = WordAnalyzer()

	def generate_phrases(self, tokens: List[str], num_phrases: int) -> List[str]:
		if len(tokens) < max(2, self.n):
			return self._generate_fallback(tokens, num_phrases)
		self.word_analyzer.analyze_word_difficulty(tokens)
		alpha_tokens = [t for t in tokens if t not in ('<START>', '<END>') and t.isalpha()]
		# Build vocabulary with difficulty filters
		from collections import Counter
		counts = Counter(alpha_tokens)
		vocab = list(dict.fromkeys(alpha_tokens))
		def in_len_range(w: str) -> bool:
			L = len(w)
			if self.difficulty == 'easy':
				return L <= 4
			if self.difficulty == 'medium':
				return 5 <= L <= 7
			return L >= 8
		vocab = [w for w in vocab if in_len_range(w)]
		# Quality filters
		if self.difficulty == 'easy':
			common_two = {"of","to","in","is","on","by","or","at","an","as","it","be","he","we","me","my","do","go","no","so","up","us"}
			filtered = []
			for w in vocab:
				L = len(w)
				if L == 2:
					if w.lower() in common_two:
						filtered.append(w)
					continue
				if L >= 3:
					if any(ch in 'aeiou' for ch in w.lower()) and counts[w] >= 2:
						filtered.append(w)
			if len(filtered) >= max(10, self._target_len()):
				vocab = filtered
		elif self.difficulty == 'medium':
			med = [w for w in vocab if counts[w] >= 2]
			if len(med) >= max(20, self._target_len()):
				vocab = med
		else:
			hard = [w for w in vocab if counts[w] >= 1]
			if len(hard) >= max(20, self._target_len()):
				vocab = hard
		# Final unique sampling
		return self._generate_unique(vocab, num_phrases)

	def _generate_unique(self, words: List[str], num_phrases: int) -> List[str]:
		phrases: List[str] = []
		used = set()
		for _ in range(num_phrases):
			target = self._target_len()
			available = [w for w in words if w not in used]
			if len(available) >= target:
				sampled = random.sample(available, target)
			elif available:
				sampled = available[:]
				remaining = target - len(sampled)
				while remaining > 0 and words:
					cand = random.choice(words)
					if sampled and cand == sampled[-1]:
						continue
					sampled.append(cand)
					remaining -= 1
			else:
				sampled = []
				for _i in range(target):
					cand = random.choice(words)
					if sampled and cand == sampled[-1]:
						continue
					sampled.append(cand)
			for w in sampled:
				used.add(w)
			phrases.append(' '.join(sampled))
		return phrases

	def _generate_fallback(self, tokens: List[str], num_phrases: int) -> List[str]:
		copy = tokens[:]
		random.shuffle(copy)
		fallback = ' '.join(copy[:10]) if copy else ''
		return [fallback for _ in range(num_phrases)]

	def _target_len(self) -> int:
		base = {'easy': 6, 'medium': 8, 'hard': 10}.get(self.difficulty, 8)
		import random as _r
		return base + _r.randint(0, 3)


