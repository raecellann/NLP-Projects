from typing import List, Tuple
from text_processor import TextProcessor
from word_analyzer import WordAnalyzer
from phrase_generator import PhraseGenerator


class Ngrams:

	def __init__(self, corpus_file: str = 'corpora/corpora.pkl', n: int = 3, num_phrases: int = 5, difficulty: str = 'medium'):
		self.corpus_file = corpus_file
		self.n = n
		self.num_phrases = num_phrases
		self.difficulty = (difficulty or 'medium').lower()
		self.text_processor = TextProcessor()
		self.word_analyzer = WordAnalyzer()
		self.phrase_generator = PhraseGenerator(n, self.difficulty)

	def generate_phrases(self) -> List[str]:
		tokens = self.text_processor.get_tokens(self.corpus_file, difficulty_section=self.difficulty)
		return self.phrase_generator.generate_phrases(tokens, self.num_phrases)

	def get_difficulty_stats(self) -> dict:
		tokens = self.text_processor.get_tokens(self.corpus_file, difficulty_section=self.difficulty)
		self.word_analyzer.analyze_word_difficulty(tokens)
		return self.word_analyzer.get_difficulty_stats()

	def get_model_stats(self) -> dict:
		tokens = self.text_processor.get_tokens(self.corpus_file, difficulty_section=self.difficulty)
		filtered = [t for t in tokens if t not in ('<START>','<END>')]
		return {
			'total_tokens': len(tokens),
			'unique_words': len(set(filtered)),
			'n_gram_order': self.n,
			'vocabulary_size': len(set(filtered)),
			'difficulty': self.difficulty,
			'difficulty_stats': self.get_difficulty_stats(),
		}

	def clear_cache(self):
		self.text_processor.clear_cache()
		self.word_analyzer.clear_cache()
		self.phrase_generator.word_analyzer.clear_cache()


