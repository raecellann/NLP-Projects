from ngrams import Ngrams
from typing_test import TypingTest
from utils import print_menu, prompt


def main():
    print("🎯 N-Gram Typing Test Generator")
    print("Generate text phrases for typing practice using n-gram language models!\n")
    
    while True:
        print_menu("Choose difficulty", [
            "Easy (2-grams, 5 phrases)",
            "Medium (3-grams, 8 phrases)",
            "Hard (4-grams, 10 phrases)",
            "Custom settings",
            "Exit"
        ])
        
        choice = prompt("\nYour choice > ")
        
        if choice == "1":
            n, phrases = 2, 5
            difficulty = "Easy"
        elif choice == "2":
            n, phrases = 3, 8
            difficulty = "Medium"
        elif choice == "3":
            n, phrases = 4, 10
            difficulty = "Hard"
        elif choice == "4":
            n, phrases = get_custom_settings()
            if n is None:
                continue
            difficulty = "Custom"
        elif choice == "5":
            print("👋 Goodbye! Happy typing!")
            return
        else:
            print("❌ Invalid choice, defaulting to Medium")
            n, phrases = 3, 8
            difficulty = "Medium"
        
        run_typing_test(n, phrases, difficulty)


def get_custom_settings():
    print("\n=== CUSTOM SETTINGS ===")
    
    try:
        n_input = prompt("Enter n-gram order (2-5): ")
        n = int(n_input)
        if n < 2 or n > 5:
            print("❌ N-gram order must be between 2 and 5")
            return None, None
            
        phrases_input = prompt("Enter number of phrases (3-15): ")
        phrases = int(phrases_input)
        if phrases < 3 or phrases > 15:
            print("❌ Number of phrases must be between 3 and 15")
            return None, None
            
        return n, phrases
        
    except ValueError:
        print("❌ Please enter valid numbers")
        return None, None


def run_typing_test(n, phrases, difficulty):
    print(f"\n🎮 Starting {difficulty} typing test...")
    print(f"   • N-gram order: {n}")
    print(f"   • Number of phrases: {phrases}")
    
    try:
        ngrams_obj = Ngrams(corpus_file="corpus.txt", n=n, num_phrases=phrases)
        
        print("\n📝 Generating phrases...")
        test_phrases = ngrams_obj.generate_phrases()
        
        if not test_phrases or all(not phrase.strip() for phrase in test_phrases):
            print("❌ Error: Could not generate valid phrases")
            print("The corpus might be too small for the selected n-gram order.")
            return
        
        print("\n📋 Generated phrases:")
        for i, phrase in enumerate(test_phrases, 1):
            if phrase.strip():
                print(f"{i}. {phrase}")
        
        test_text = " ".join(phrase for phrase in test_phrases if phrase.strip())
        
        if not test_text.strip():
            print("❌ Error: No valid text generated for typing test")
            return
        
        print(f"\n🎯 Ready to start typing test!")
        game = TypingTest(test_text)
        game.start()
        
    except FileNotFoundError:
        print("❌ Error: corpus.txt file not found!")
        print("Please make sure the corpus file exists in the current directory.")
    except Exception as e:
        print(f"❌ Error running typing test: {e}")


if __name__ == "__main__":
    main()
