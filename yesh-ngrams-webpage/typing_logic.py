from __future__ import annotations
import time
from typing import List, Tuple, Dict, Union, Optional
from backend import TypingTest


class TypingTestLogic:
    def __init__(self):
        self.typing_test = TypingTest()
        self.test_duration: int = 60
        self.test_start_ms: int = 0
        self.is_active: bool = False
        self.test_started_once: bool = False
        self.current_text: str = ''
        self.words: List[str] = []
        self.current_word_index: int = 0
        self.typed_words: List[str] = []
        self.incorrect_words: List[Tuple[str, str, int]] = []
        self.final_results: Dict[str, Union[int, float, str, List]] = {}
        self.test_end_ms: int = 0
        self._load_sample_text()

    def _load_sample_text(self) -> None:
        try:
            self.current_text = self.typing_test.get_random_text(use_ngrams=True, length=30)
            if not self.current_text:
                self.current_text = self.typing_test.get_random_text(use_ngrams=False, length=30)
            self.words = self.current_text.split()
            self.current_word_index = 0
            self.typed_words = []
            self.incorrect_words = []
        except Exception:
            self.current_text = "The quick brown fox jumps over the lazy dog. This is a sample text for typing practice."
            self.words = self.current_text.split()
            self.current_word_index = 0
            self.typed_words = []
            self.incorrect_words = []

    def _load_new_text(self) -> None:
        try:
            self.current_text = self.typing_test.get_random_text(use_ngrams=True, length=30)
            if not self.current_text:
                self.current_text = self.typing_test.get_random_text(use_ngrams=False, length=30)
            self.words = self.current_text.split()
            self.current_word_index = 0
            self.typed_words = []
            self.incorrect_words = []
        except Exception:
            self.current_text = "The quick brown fox jumps over the lazy dog. This is a sample text for typing practice."
            self.words = self.current_text.split()
            self.current_word_index = 0
            self.typed_words = []
            self.incorrect_words = []

    def start_test(self) -> None:
        if self.is_active:
            return
        self.is_active = True
        self.test_started_once = True
        self.test_start_ms = int(time.time() * 1000)
        self.current_word_index = 0
        self.typed_words = []
        self.incorrect_words = []
        self.final_results = {}

    def end_test(self) -> None:
        if self.is_active:
            self.is_active = False
            self.test_end_ms = int(time.time() * 1000)
            self._calculate_final_results()

    def reset_test(self) -> None:
        self.is_active = False
        self.test_started_once = False
        self.test_start_ms = 0
        self.test_end_ms = 0
        self.final_results = {}
        self.current_word_index = 0
        self.typed_words = []
        self.incorrect_words = []
        self._load_sample_text()

    def reset_current_word(self):
        if self.current_word_index > 0:
            self.current_word_index -= 1
            if self.typed_words:
                self.typed_words.pop()
            if self.incorrect_words and self.incorrect_words[-1][2] == self.current_word_index:
                self.incorrect_words.pop()

    def new_test(self) -> None:
        self.reset_test()
        self.start_test()

    def set_test_duration(self, duration: int) -> None:
        self.test_duration = duration

    def _calculate_final_results(self) -> None:
        if not self.test_started_once or self.test_start_ms == 0:
            self.final_results = {}
            return

        end_time = self.test_end_ms if self.test_end_ms > 0 else int(time.time() * 1000)
        elapsed = (end_time - self.test_start_ms) / 1000.0
        
        word_count = len(self.typed_words)
        minutes = elapsed / 60.0
        wpm = int(round(word_count / minutes)) if minutes > 0 else 0
        
        if self.current_word_index == 0:
            accuracy = 100
        else:
            correct_words = self.current_word_index - len(self.incorrect_words)
            accuracy = int(round((correct_words / self.current_word_index) * 100))
        
        self.final_results = {
            'wpm': wpm,
            'accuracy': accuracy,
            'time_taken': round(elapsed, 2),
            'word_count': word_count,
            'char_count': len(' '.join(self.typed_words)),
            'incorrect_words': self.incorrect_words
        }

    def elapsed_seconds(self) -> float:
        if not self.is_active:
            return 0.0
        return (int(time.time() * 1000) - self.test_start_ms) / 1000.0

    def remaining_seconds(self) -> float:
        elapsed = self.elapsed_seconds()
        return max(0.0, self.test_duration - elapsed)

    def calculate_current_wpm(self, elapsed: float) -> int:
        if elapsed <= 0:
            return 0
        typed = len(self.typed_words)
        minutes = elapsed / 60.0
        return int(round(typed / minutes)) if minutes > 0 else 0

    def calculate_current_accuracy(self) -> int:
        if self.current_word_index == 0:
            return 100
        correct_words = self.current_word_index - len(self.incorrect_words)
        return int(round((correct_words / self.current_word_index) * 100))

    def process_word_input(self, word: str) -> bool:
        if not self.is_active:
            return False
        if not word or not word.strip():
            return False
        word_clean = word.strip()
        self.typed_words.append(word_clean)
        expected = self.words[self.current_word_index]
        if word_clean != expected:
            self.incorrect_words.append((expected, word_clean, self.current_word_index))
        self.current_word_index += 1
        return True

    def skip_current_word(self) -> bool:
        if self.current_word_index >= len(self.words):
            return False
        expected = self.words[self.current_word_index]
        self.incorrect_words.append((expected, "", self.current_word_index))
        self.current_word_index += 1
        return True

    def check_test_end(self) -> bool:
        if not self.is_active:
            return False
        if self.remaining_seconds() <= 0:
            self.end_test()
            return True
        return False

    def is_test_completed(self) -> bool:
        return not self.is_active and self.test_started_once

    def get_test_status(self) -> str:
        return "completed" if not self.is_active and self.test_started_once else "active"
