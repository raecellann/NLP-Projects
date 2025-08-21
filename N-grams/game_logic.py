"""
Game Logic for the N-Grams Typing Test application.
Contains core game mechanics and logic separate from UI.
"""

import time
from typing import Tuple
from constants import DIFFICULTY_SETTINGS
from ngrams import Ngrams


class GameLogic:
    """Core game logic and mechanics."""
    
    def __init__(self):
        self.typing_text = ""
        self.target_text = ""
        self.start_time = 0
        self.is_typing = False
        self.current_char_index = 0
        self.correct_chars = 0
        self.total_chars = 0
        self.wpm = 0
        self.accuracy = 0
        self.elapsed_time = 0
        self.difficulty = "Medium"
        self.n_gram = 3
        self.num_phrases = 8
        self.time_limit = 60
        self.time_remaining = self.time_limit
        self.base_target_len = 8
        self.avg_word_len = 6.0
        self.ngrams_obj = None
        self.render_start_index = 0
    
    def start_game(self, difficulty: str):
        """Start a new game with the specified difficulty."""
        self.difficulty = difficulty
        settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["Medium"])
        
        self.n_gram = settings["n_gram"]
        self.base_target_len = settings["base_target_len"]
        self.avg_word_len = settings["avg_word_len"]
        
        try:
            # Calculate required phrases based on time limit
            approx_chars_per_phrase = int(self.base_target_len * (self.avg_word_len + 1))
            min_chars = int(self.time_limit * 8)
            num_phrases = max(5, min(40, (min_chars + approx_chars_per_phrase - 1) // approx_chars_per_phrase))
            
            # Generate initial text
            self.ngrams_obj = Ngrams(
                corpus_file="corpora/corpora.pkl", 
                n=self.n_gram, 
                num_phrases=num_phrases, 
                difficulty=self.difficulty.lower()
            )
            test_phrases = self.ngrams_obj.generate_phrases()
            self.target_text = " ".join(phrase for phrase in test_phrases if phrase.strip())
            
            # Ensure minimum text length
            if len(self.target_text) < min_chars:
                extra_needed = min_chars - len(self.target_text)
                extra_phrases = max(3, (extra_needed + approx_chars_per_phrase - 1) // approx_chars_per_phrase)
                tmp = Ngrams(
                    corpus_file="corpora/corpora.pkl", 
                    n=self.n_gram, 
                    num_phrases=extra_phrases, 
                    difficulty=self.difficulty.lower()
                )
                test_phrases += tmp.generate_phrases()
                self.target_text = " ".join(phrase for phrase in test_phrases if phrase.strip())
            
            self.total_chars = len(self.target_text)
            self.typing_text = ""
            self.current_char_index = 0
            self.correct_chars = 0
            self.is_typing = False
            self.time_remaining = float(self.time_limit)
            self.render_start_index = 0
            
        except Exception as e:
            print(f"Error generating text: {e}")
            # Fallback text
            self.target_text = "The quick brown fox jumps over the lazy dog. This is a sample text for typing practice."
            self.total_chars = len(self.target_text)
    
    def handle_typing(self, event) -> Tuple[bool, str]:
        """Handle typing input and return (success, message)."""
        if event.key == 8:  # pygame.K_BACKSPACE
            if self.typing_text:
                self.typing_text = self.typing_text[:-1]
                self._recalculate_correct_chars()
                return True, "backspace"
        elif event.key == 13:  # pygame.K_RETURN
            return True, "return"
        else:
            if not self.is_typing:
                self.is_typing = True
                self.start_time = time.time()
            
            char = event.unicode
            if char.isprintable():
                self.typing_text += char
                
                if len(self.typing_text) <= len(self.target_text):
                    if char == self.target_text[len(self.typing_text) - 1]:
                        self.correct_chars += 1
                        return True, "correct"
                    else:
                        return True, "incorrect"
                
                # Check if we need to refill text
                remaining_chars = len(self.target_text) - len(self.typing_text)
                if self.is_typing and self.time_remaining > 0.2 and remaining_chars < 150:
                    self._refill_target_text()
                
                # Check if game is complete
                if len(self.typing_text) >= len(self.target_text):
                    if self.is_typing and self.time_remaining > 0.2:
                        self._refill_target_text()
                    else:
                        return False, "game_complete"
                
                return True, "typed"
        
        return True, "processed"
    
    def _recalculate_correct_chars(self):
        """Recalculate correct characters after backspace."""
        self.correct_chars = 0
        for i in range(len(self.typing_text)):
            if i < len(self.target_text) and self.typing_text[i] == self.target_text[i]:
                self.correct_chars += 1
    
    def _refill_target_text(self):
        """Add more text to continue the game."""
        try:
            approx_chars_per_phrase = int(self.base_target_len * (self.avg_word_len + 1)) or 20
            needed_chars = max(200, int(self.time_remaining * 8))
            extra_phrases = max(3, min(40, (needed_chars + approx_chars_per_phrase - 1) // approx_chars_per_phrase))
            
            generator = Ngrams(
                corpus_file="corpora/corpora.pkl", 
                n=self.n_gram, 
                num_phrases=extra_phrases, 
                difficulty=self.difficulty.lower()
            )
            more_phrases = generator.generate_phrases()
            extra_text = " ".join(p for p in more_phrases if p.strip())
            
            if extra_text:
                if self.target_text and not self.target_text.endswith(" "):
                    self.target_text += " "
                self.target_text += extra_text
                self.total_chars = len(self.target_text)
                
        except Exception as e:
            # Fallback text
            fallback = " keep typing to improve your speed and accuracy."
            self.target_text += fallback
            self.total_chars = len(self.target_text)
    
    def end_game(self):
        """End the current game and calculate final statistics."""
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.elapsed_time = min(elapsed, float(self.time_limit))
        else:
            self.elapsed_time = float(self.time_limit)
        
        # Calculate WPM
        elapsed_minutes = self.elapsed_time / 60
        if elapsed_minutes > 0:
            self.wpm = (self.correct_chars / 5) / elapsed_minutes
        else:
            self.wpm = 0
        
        # Calculate accuracy
        typed_chars = len(self.typing_text)
        if typed_chars > 0:
            self.accuracy = (self.correct_chars / typed_chars) * 100
        else:
            self.accuracy = 0
    
    def get_progress(self) -> float:
        """Get current progress as a percentage."""
        if self.total_chars > 0:
            return self.correct_chars / self.total_chars
        return 0.0
    
    def get_accuracy(self) -> float:
        """Get current accuracy as a percentage."""
        if len(self.typing_text) > 0:
            return (self.correct_chars / len(self.typing_text)) * 100
        return 0.0
    
    def get_time_remaining(self) -> float:
        """Get time remaining in the game."""
        if self.is_typing:
            elapsed = time.time() - self.start_time
            return max(0, self.time_limit - elapsed)
        return self.time_limit
    
    def reset_game(self):
        """Reset the game state."""
        self.typing_text = ""
        self.target_text = ""
        self.start_time = 0
        self.is_typing = False
        self.current_char_index = 0
        self.correct_chars = 0
        self.total_chars = 0
        self.wpm = 0
        self.accuracy = 0
        self.elapsed_time = 0
        self.time_remaining = self.time_limit
        self.render_start_index = 0
