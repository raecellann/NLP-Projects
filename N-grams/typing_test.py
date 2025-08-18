import time
import sys
import threading
from ngrams import Ngrams


class TypingTest:
    
    def __init__(self, text: str, time_limit: int):
        self.text = text
        self.time_limit = time_limit
        self.start_time = None
        self.end_time = None
        self.user_input = ""
        self.test_running = False
        self.time_remaining = time_limit
    
    def start(self):
        print("\n" + "="*60)
        print("🎯 TYPING TEST STARTED")
        print(f"⏰ Time Limit: {self.time_limit} seconds")
        print("="*60)
        print(f"Text to type:\n")
        print(f'"{self.text}"')
        print("\n" + "="*60)
        print("Start typing NOW! Timer will start automatically...")
        print("="*60 + "\n")
        
        # Start countdown timer in background
        timer_thread = threading.Thread(target=self.countdown_timer)
        timer_thread.daemon = True
        timer_thread.start()
        
        self.start_time = time.time()
        self.test_running = True
        
        # Get user input with timer
        try:
            self.user_input = input("Type here: ")
        except KeyboardInterrupt:
            print("\n\n⏹️ Test interrupted by user")
            self.test_running = False
            return
        
        self.end_time = time.time()
        self.test_running = False
        
        self.show_results()
    
    def countdown_timer(self):
        """Countdown timer that runs in background"""
        time.sleep(1)  # Wait for user to start typing
        
        while self.test_running and self.time_remaining > 0:
            if self.time_remaining <= 10:
                print(f"\n⏰ {self.time_remaining} seconds remaining!")
            elif self.time_remaining % 15 == 0:
                print(f"\n⏰ {self.time_remaining} seconds remaining")
            
            time.sleep(1)
            self.time_remaining -= 1
            
            if self.time_remaining <= 0:
                print("\n\n⏰ TIME'S UP! Test finished!")
                self.test_running = False
                break
    
    def show_results(self):
        if not self.start_time:
            print("❌ Test not completed properly")
            return
        
        duration = self.end_time - self.start_time if self.end_time else self.time_limit
        words_typed = len(self.user_input.split())
        characters_typed = len(self.user_input)
        
        # Calculate WPM (Words Per Minute)
        wpm = (words_typed / duration) * 60 if duration > 0 else 0
        
        # Calculate accuracy
        accuracy = self.calculate_accuracy()
        
        print("\n" + "="*60)
        print("📊 TYPING TEST RESULTS")
        print("="*60)
        print(f"Time used: {duration:.2f} seconds")
        print(f"Words typed: {words_typed}")
        print(f"Characters typed: {characters_typed}")
        print(f"Speed: {wpm:.1f} WPM")
        print(f"Accuracy: {accuracy:.1f}%")
        print("="*60)
        
        if accuracy >= 95:
            print("🎉 Excellent accuracy!")
        elif accuracy >= 85:
            print("👍 Good accuracy!")
        elif accuracy >= 70:
            print("😐 Fair accuracy, keep practicing!")
        else:
            print("💪 Keep practicing to improve!")
    
    def calculate_accuracy(self) -> float:
        if not self.text or not self.user_input:
            return 0.0
        
        # Simple character-by-character accuracy
        correct_chars = 0
        max_len = max(len(self.text), len(self.user_input))
        
        for i in range(max_len):
            if i < len(self.text) and i < len(self.user_input):
                if self.text[i] == self.user_input[i]:
                    correct_chars += 1
        
        return (correct_chars / max_len) * 100 if max_len > 0 else 0


def run_typing_test_with_ngrams(difficulty: str = "medium", time_limit: int = 60):
    """Run a typing test using n-grams generated text with countdown timer."""
    try:
        print(f"🎮 Generating {difficulty.capitalize()} difficulty text...")
        
        # Adjust n-gram settings based on difficulty and time
        if difficulty == "easy":
            n = 2
            base_target_len = 6
            avg_word_len = 3.5
        elif difficulty == "medium":
            n = 3
            base_target_len = 8
            avg_word_len = 6.0
        else:  # hard
            n = 4
            base_target_len = 10
            avg_word_len = 8.0
        # Estimate phrases to fit time_limit
        approx_chars_per_phrase = int(base_target_len * (avg_word_len + 1))
        min_chars = int(time_limit * 8)  # baseline 8 chars/sec of content
        num_phrases = max(5, min(40, (min_chars + approx_chars_per_phrase - 1) // approx_chars_per_phrase))
        
        ngrams_obj = Ngrams(corpus_file="corpora/corpora.pkl", n=n, num_phrases=num_phrases, difficulty=difficulty)
        phrases = ngrams_obj.generate_phrases()
        
        if not phrases:
            print("❌ Could not generate text for typing test")
            return
        
        # Combine phrases into one text
        test_text = " ".join(phrases)
        # If still short, top up by generating more phrases once
        if len(test_text) < min_chars:
            extra_needed = min_chars - len(test_text)
            extra_phrases = max(3, (extra_needed + approx_chars_per_phrase - 1) // approx_chars_per_phrase)
            ngrams_obj = Ngrams(corpus_file="corpora/corpora.pkl", n=n, num_phrases=extra_phrases, difficulty=difficulty)
            phrases += ngrams_obj.generate_phrases()
            test_text = " ".join(phrases)
        
        if not test_text.strip():
            print("❌ Generated text is empty")
            return
        
        print(f"✅ Generated text ({len(test_text)} characters)")
        
        # Start typing test with countdown
        test = TypingTest(test_text, time_limit)
        test.start()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🎯 N-Grams Typing Test (MonkeyType Style)")
    print("="*50)
    
    while True:
        print("\nChoose difficulty:")
        print("1. Easy (basic words)")
        print("2. Medium (moderate words)")
        print("3. Hard (complex words)")
        print("4. Exit")
        
        choice = input("\nYour choice (1-4): ").strip()
        
        if choice == "4":
            print("👋 Goodbye! Happy typing!")
            break
        elif choice not in ["1", "2", "3"]:
            print("❌ Invalid choice, please try again")
            continue
        
        # Choose time limit
        print("\nChoose time limit:")
        print("1. 30 seconds (quick test)")
        print("2. 60 seconds (standard test)")
        print("3. 120 seconds (long test)")
        
        time_choice = input("Time choice (1-3): ").strip()
        
        if time_choice == "1":
            time_limit = 30
        elif time_choice == "2":
            time_limit = 60
        elif time_choice == "3":
            time_limit = 120
        else:
            print("❌ Invalid time choice, using 60 seconds")
            time_limit = 60
        
        # Set difficulty
        if choice == "1":
            difficulty = "easy"
        elif choice == "2":
            difficulty = "medium"
        else:
            difficulty = "hard"
        
        # Run the test
        run_typing_test_with_ngrams(difficulty, time_limit)
        
        # Ask if user wants to continue
        print("\n" + "="*50)
        continue_choice = input("Take another test? (y/n): ").strip().lower()
        if continue_choice != 'y':
            print("👋 Goodbye! Happy typing!")
            break
