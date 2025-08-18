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
            # Prefer canonical names; also support synonyms
            synonym_map = {
                "easy": ["easy", "basic", "simple", "short"],
                "medium": ["medium", "moderate"],
                "hard": ["hard", "difficult", "deep", "long"]
            }
            candidates = synonym_map.get(canonical, [canonical])
            # If target section exists, build exclusive list by subtracting easier tiers
            for cand in candidates:
                if cand in lower_map:
                    target_key = lower_map[cand]
                    target_val = data[target_key]
                    # Build exclusive content for list/tuple types by removing overlaps with easier sets
                    if isinstance(target_val, (list, tuple)):
                        target_list = [str(item) for item in target_val]
                        # Determine easier sections to subtract
                        easier_sections = []
                        if canonical == "medium":
                            easier_sections = ["easy", "basic", "simple", "short"]
                        elif canonical == "hard":
                            easier_sections = ["easy", "basic", "simple", "short", "medium", "moderate"]
                        # Normalize helper
                        def _norm(s: str) -> str:
                            return " ".join(s.split()).strip().lower()
                        to_remove = set()
                        for ez in easier_sections:
                            if ez in lower_map and isinstance(data[lower_map[ez]], (list, tuple)):
                                to_remove.update(_norm(str(item)) for item in data[lower_map[ez]])
                        # Build exclusive and deduplicated (normalized) in-order
                        seen_norm = set()
                        exclusive_items = []
                        for s in target_list:
                            n = _norm(s)
                            if n in to_remove or n in seen_norm:
                                continue
                            seen_norm.add(n)
                            exclusive_items.append(s)
                        exclusive = exclusive_items
                        return "\n".join(exclusive)
                    # If it's a string, just return it (can't subtract safely)
                    if isinstance(target_val, str):
                        return target_val
            # If exact section not found, fall back to concatenating all
        
        # Fallback: concatenate everything
        if isinstance(data, str):
            return data
        if isinstance(data, (list, tuple)):
            return "\n".join(str(item) for item in data)
        if isinstance(data, dict):
            collected_parts = []
            for value in data.values():
                if isinstance(value, str):
                    collected_parts.append(value)
                elif isinstance(value, (list, tuple)):
                    collected_parts.append("\n".join(str(item) for item in value))
            return "\n".join(collected_parts)
        raise ValueError("Unsupported data type in corpus.")

    def load_text(self, corpus_file: str, difficulty_section: Optional[str] = None) -> str:
        if self._text_cache is not None:
            return self._text_cache
        
        try:
            if corpus_file.lower().endswith(".pkl"):
                with open(corpus_file, "rb") as f:
                    data = pickle.load(f)
                    content = self._extract_section_text(data, difficulty_section)
            else:
                with open(corpus_file, "r", encoding="utf-8") as f:
                    content = f.read()
            
            if not content or not str(content).strip():
                raise ValueError("Corpus file is empty.")
            
            self._text_cache = str(content)
            return self._text_cache
        except FileNotFoundError:
            raise FileNotFoundError(f"Corpus file '{corpus_file}' not found!")
    
    def tokenize(self, text: str, special_tokens: bool = True) -> List[str]:
        if not text or not text.strip():
            return []
        
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        tokens = []
        
        for sent in sentences:
            if not sent:
                continue
            
            if special_tokens:
                tokens.append("<START>")
            
            words = re.findall(r"\w+|[^\w\s]", sent)
            tokens.extend(words)
            
            if special_tokens:
                tokens.append("<END>")
        
        return tokens
    
    def get_tokens(self, corpus_file: str, difficulty_section: Optional[str] = None) -> List[str]:
        if self._tokens_cache is not None:
            return self._tokens_cache
        
        text = self.load_text(corpus_file, difficulty_section=difficulty_section)
        tokens = self.tokenize(text, special_tokens=True)
        self._tokens_cache = tokens
        return tokens
    
    def detokenize(self, tokens: List[str]) -> str:
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
    
    def clear_cache(self):
        self._text_cache = None
        self._tokens_cache = None
