import re
import pickle
from typing import List, Optional, Union


class TextProcessor:

	def __init__(self):
		self._text_cache: Optional[str] = None
		self._tokens_cache: Optional[List[str]] = None

	def _extract_section_text(self, data: Union[str, List, tuple, dict], section: Optional[str]) -> str:
		if section and isinstance(data, dict):
			# Normalize keys
			lower_map = {str(k).lower(): k for k in data.keys()}
			canonical = section.lower()
			# Synonyms
			synonym_map = {
				"easy": ["easy", "basic", "simple", "short"],
				"medium": ["medium", "moderate"],
				"hard": ["hard", "difficult", "deep", "long"],
			}
			candidates = synonym_map.get(canonical, [canonical])
			for cand in candidates:
				if cand in lower_map:
					target_key = lower_map[cand]
					target_val = data[target_key]
					if isinstance(target_val, (list, tuple)):
						return "\n".join(str(item) for item in target_val)
					if isinstance(target_val, str):
						return target_val
		# Fallback: concatenate everything
		if isinstance(data, str):
			return data
		if isinstance(data, (list, tuple)):
			return "\n".join(str(item) for item in data)
		if isinstance(data, dict):
			parts = []
			for value in data.values():
				if isinstance(value, str):
					parts.append(value)
				elif isinstance(value, (list, tuple)):
					parts.append("\n".join(str(item) for item in value))
			return "\n".join(parts)
		raise ValueError("Unsupported data type in corpus.")

	def load_text(self, corpus_file: str, difficulty_section: Optional[str] = None) -> str:
		if self._text_cache is not None:
			return self._text_cache
		if corpus_file.lower().endswith('.pkl'):
			with open(corpus_file, 'rb') as f:
				data = pickle.load(f)
				content = self._extract_section_text(data, difficulty_section)
		else:
			with open(corpus_file, 'r', encoding='utf-8') as f:
				content = f.read()
		if not content or not str(content).strip():
			raise ValueError('Corpus file is empty.')
		self._text_cache = str(content)
		return self._text_cache

	def tokenize(self, text: str, special_tokens: bool = True) -> List[str]:
		if not text or not text.strip():
			return []
		sentences = re.split(r'(?<=[.!?])\s+', text.strip())
		tokens: List[str] = []
		for sent in sentences:
			if not sent:
				continue
			if special_tokens:
				tokens.append('<START>')
			words = re.findall(r"\w+|[^\w\s]", sent)
			tokens.extend(words)
			if special_tokens:
				tokens.append('<END>')
		return tokens

	def get_tokens(self, corpus_file: str, difficulty_section: Optional[str] = None) -> List[str]:
		if self._tokens_cache is not None:
			return self._tokens_cache
		text = self.load_text(corpus_file, difficulty_section=difficulty_section)
		tokens = self.tokenize(text, special_tokens=True)
		self._tokens_cache = tokens
		return tokens

	def clear_cache(self):
		self._text_cache = None
		self._tokens_cache = None


