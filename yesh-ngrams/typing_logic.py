import pygame
from typing import List, Tuple
from backend import TypingTest


class TypingTestLogic:
    def __init__(self):
        # Backend typing test logic
        self.typing_test = TypingTest()

        # Test state
        self.test_duration = 60
        self.test_start_ms = 0
        self.is_active = False
        self.test_started_once = False

        # Text state
        self.current_text = ''
        self.words: List[str] = []
        self.current_word_index = 0
        self.typed_words: List[str] = []
        self.incorrect_words: List[Tuple[str, str, int]] = []

        # Results storage
        self.final_results = {}
        self.test_end_ms = 0

        # Preload a sample text
        self._load_sample_text()

    def _load_sample_text(self):
        # Prefer n-gram generated text; fall back to random
        self.current_text = self.typing_test.get_random_text(use_ngrams=True, length=30)
        if not self.current_text:
            self.current_text = self.typing_test.get_random_text(use_ngrams=False, length=30)
        self.words = self.current_text.split()
        self.current_word_index = 0
        self.typed_words = []
        self.incorrect_words = []

    def _load_new_text(self):
        # Similar behavior to web: often pick a different corpora text, or generate via n-grams
        self.current_text = self.typing_test.get_random_text(use_ngrams=True, length=30)
        if not self.current_text:
            self.current_text = self.typing_test.get_random_text(use_ngrams=False, length=30)
        self.words = self.current_text.split()
        self.current_word_index = 0
        self.typed_words = []
        self.incorrect_words = []

    # Test controls
    def start_test(self):
        if self.is_active:
            return
        self.is_active = True
        self.test_started_once = True
        self.test_start_ms = pygame.time.get_ticks()
        self.current_word_index = 0
        self.typed_words = []
        self.incorrect_words = []
        # Clear previous results when starting new test
        self.final_results = {}

    def end_test(self):
        if self.is_active:
            self.is_active = False
            self.test_end_ms = pygame.time.get_ticks()
            # Calculate and store final results
            self._calculate_final_results()

    def reset_test(self):
        self.is_active = False
        self.test_started_once = False
        self.test_start_ms = 0
        self.test_end_ms = 0
        self.final_results = {}
        self._load_sample_text()

    def new_test(self):
        self.reset_test()
        self.start_test()

    def set_test_duration(self, duration: int):
        self.test_duration = duration

    def _calculate_final_results(self):
        """Calculate and store the final test results"""
        if not self.test_started_once or self.test_start_ms == 0:
            self.final_results = {}
            return

        # Use test_end_ms if available, otherwise current time
        end_time = self.test_end_ms if self.test_end_ms > 0 else pygame.time.get_ticks()
        elapsed = (end_time - self.test_start_ms) / 1000.0
        
        # Calculate WPM
        word_count = len(self.typed_words)
        minutes = elapsed / 60.0
        wpm = int(round(word_count / minutes)) if minutes > 0 else 0
        
        # Calculate accuracy
        if self.current_word_index == 0:
            accuracy = 100
        else:
            correct_words = self.current_word_index - len(self.incorrect_words)
            accuracy = int(round((correct_words / self.current_word_index) * 100))
        
        # Store the results
        self.final_results = {
            'wpm': wpm,
            'accuracy': accuracy,
            'time_taken': round(elapsed, 2),
            'word_count': word_count,
            'char_count': len(' '.join(self.typed_words)),
            'incorrect_words': self.incorrect_words
        }

    # Stats calculations
    def elapsed_seconds(self) -> float:
        if not self.is_active:
            return 0.0
        return (pygame.time.get_ticks() - self.test_start_ms) / 1000.0

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
        return int(round((correct_words / self.current_word_index) * 100)) if self.current_word_index > 0 else 100

    # Word processing
    def process_word_input(self, word: str):
        if not self.is_active:
            return

        # Skip empty words (just spaces)
        if not word.strip():
            return

        # Add the word to typed words list
        self.typed_words.append(word.strip())
        
        # Check if the word is correct
        expected = self.words[self.current_word_index] if self.current_word_index < len(self.words) else ''
        if word.strip() != expected:
            self.incorrect_words.append((expected, word.strip(), self.current_word_index))

        self.current_word_index += 1

        # If we've completed all words, load more text
        if self.current_word_index >= len(self.words):
            self._load_new_text()

    def check_test_end(self) -> bool:
        if not self.is_active:
            return False
        if self.remaining_seconds() <= 0:
            self.end_test()  # This will calculate and store final results
            return True
        return False

    def get_results(self) -> dict:
        """Get the stored final results"""
        if not self.final_results:
            # If no final results, calculate current results
            if self.test_started_once and self.test_start_ms > 0:
                elapsed = self.elapsed_seconds()
                
                # Calculate WPM
                word_count = len(self.typed_words)
                minutes = elapsed / 60.0
                wpm = int(round(word_count / minutes)) if minutes > 0 else 0
                
                # Calculate accuracy
                if self.current_word_index == 0:
                    accuracy = 100
                else:
                    correct_words = self.current_word_index - len(self.incorrect_words)
                    accuracy = int(round((correct_words / self.current_word_index) * 100))
                
                return {
                    'wpm': wpm,
                    'accuracy': accuracy,
                    'time_taken': round(elapsed, 2),
                    'word_count': word_count,
                    'char_count': len(' '.join(self.typed_words)),
                    'incorrect_words': self.incorrect_words
                }
            return {}
        
        return self.final_results

    # Getters
    def get_current_text(self) -> str:
        return self.current_text

    def get_words(self) -> List[str]:
        return self.words

    def get_current_word_index(self) -> int:
        return self.current_word_index

    def get_typed_words(self) -> List[str]:
        return self.typed_words

    def get_incorrect_words(self) -> List[Tuple[str, str, int]]:
        return self.incorrect_words

    def is_test_active(self) -> bool:
        return self.is_active

    def has_test_started_once(self) -> bool:
        return self.test_started_once

    def get_test_duration(self) -> int:
        return self.test_duration
