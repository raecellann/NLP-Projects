import time
from typing import List, Tuple


class TypingTest:
    def __init__(self, test_text: str):
        self.test_text = test_text.strip()
        self.original_words = self.test_text.split()
        
    def start(self):
        if not self.test_text:
            print("❌ Error: No text provided for typing test")
            return
            
        print("\n" + "="*60)
        print("🎯 TYPING TEST")
        print("="*60)
        print("\nType the following text exactly as shown:")
        print("-" * 50)
        print(self.test_text)
        print("-" * 50)
        
        input("\nPress ENTER when you're ready to start typing...")
        
        print("\n⏱️  Starting timer... Type now!")
        print("-" * 50)
        
        start_time = time.time()
        try:
            typed_text = input("> ")
        except KeyboardInterrupt:
            print("\n❌ Test cancelled by user")
            return
        except Exception as e:
            print(f"\n❌ Error during typing: {e}")
            return
            
        end_time = time.time()
        
        self._calculate_and_display_results(typed_text, start_time, end_time)

    def _calculate_and_display_results(self, typed_text: str, start_time: float, end_time: float):
        elapsed_time = end_time - start_time
        elapsed_minutes = elapsed_time / 60
        
        if elapsed_minutes <= 0:
            print("❌ Error: Invalid timing data")
            return
            
        typed_words = typed_text.split()
        
        correct_count = self._count_correct_words(typed_words)
        total_original_words = len(self.original_words)
        
        if total_original_words == 0:
            print("❌ Error: No words in original text")
            return
            
        accuracy = (correct_count / total_original_words) * 100
        
        wpm = correct_count / elapsed_minutes
        
        self._display_results(elapsed_time, accuracy, wpm, correct_count, total_original_words)
        
        self._provide_feedback(accuracy, wpm)

    def _count_correct_words(self, typed_words: List[str]) -> int:
        correct_count = 0
        min_length = min(len(typed_words), len(self.original_words))
        
        for i in range(min_length):
            if typed_words[i] == self.original_words[i]:
                correct_count += 1
                
        return correct_count

    def _display_results(self, elapsed_time: float, accuracy: float, wpm: float, 
                        correct_count: int, total_words: int):
        print("\n" + "="*60)
        print("📊 TYPING TEST RESULTS")
        print("="*60)
        
        print(f"⏱️  Time Taken:     {elapsed_time:.2f} seconds")
        print(f"📝 Words Typed:    {correct_count}/{total_words}")
        print(f"🎯 Accuracy:       {accuracy:.1f}%")
        print(f"⚡ Speed:          {wpm:.1f} WPM")
        
        if elapsed_time > 0:
            print(f"📈 Characters/sec: {len(' '.join(self.original_words[:correct_count])) / elapsed_time:.1f}")
        
        print("="*60)

    def _provide_feedback(self, accuracy: float, wpm: float):
        print("\n💬 Performance Feedback:")
        
        if accuracy >= 95:
            print("   🏆 Excellent accuracy! You're very precise!")
        elif accuracy >= 85:
            print("   👍 Great accuracy! Keep up the good work!")
        elif accuracy >= 70:
            print("   ✅ Good accuracy! A bit more practice will help.")
        elif accuracy >= 50:
            print("   ⚠️  Fair accuracy. Try to be more careful with spelling.")
        else:
            print("   📚 Accuracy needs improvement. Focus on accuracy over speed.")
        
        if wpm >= 60:
            print("   🚀 Lightning fast! You're a speed demon!")
        elif wpm >= 40:
            print("   ⚡ Fast typing! Great speed!")
        elif wpm >= 25:
            print("   🎯 Good speed! You're doing well!")
        elif wpm >= 15:
            print("   📖 Moderate speed. Practice will help you improve.")
        else:
            print("   🐌 Slow but steady! Focus on building muscle memory.")
        
        print(f"\n🎯 Overall Assessment:")
        if accuracy >= 90 and wpm >= 40:
            print("   🌟 Outstanding performance! You're a typing master!")
        elif accuracy >= 80 and wpm >= 30:
            print("   👍 Very good performance! Keep practicing!")
        elif accuracy >= 70 and wpm >= 20:
            print("   ✅ Good performance! Room for improvement.")
        else:
            print("   📚 Keep practicing! Both speed and accuracy will improve with time.")
        
        print(f"\n💡 Tip: Regular practice is the key to improving your typing skills!")
