from ngrams import Ngrams
from utils import print_menu, prompt, format_frequency_table, validate_input


def demo_word_frequencies():
    print("=== WORD FREQUENCY & NEXT WORD PREDICTION DEMO ===\n")
    
    try:
        ngrams_obj = Ngrams(corpus_file="corpus.txt", n=3, num_phrases=5)
        print("✅ N-gram model loaded successfully!")
        
        stats = ngrams_obj.get_model_stats()
        print(f"\n📊 Model Statistics:")
        print(f"   • Total tokens: {stats['total_tokens']}")
        print(f"   • Unique words: {stats['unique_words']}")
        print(f"   • N-gram order: {stats['n_gram_order']}")
        print(f"   • Vocabulary size: {stats['vocabulary_size']}")
        
    except FileNotFoundError:
        print("❌ Error: corpus.txt file not found!")
        print("Please make sure the corpus file exists in the current directory.")
        return
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    while True:
        print_menu("Choose an option", [
            "See word frequencies (unigrams)",
            "Predict next word after a phrase",
            "Show all possible next words with frequencies",
            "View model statistics",
            "Exit"
        ])
        
        choice = prompt("\nYour choice > ")
        
        if choice == "1":
            show_unigram_frequencies(ngrams_obj)
        elif choice == "2":
            predict_next_word(ngrams_obj)
        elif choice == "3":
            show_all_next_words(ngrams_obj)
        elif choice == "4":
            show_model_statistics(ngrams_obj)
        elif choice == "5":
            print("Salamat bitch! 👋")
            break
        else:
            print("❌ Invalid choice, please try again!")


def show_unigram_frequencies(ngrams_obj):
    print("\n=== MOST COMMON WORDS (UNIGRAMS) ===")
    
    try:
        word_freqs = ngrams_obj.get_word_frequencies(top_k=20)
        
        if not word_freqs:
            print("No word frequency data available.")
            return
            
        table = format_frequency_table(word_freqs, "Most Common Words")
        print(table)
        
    except Exception as e:
        print(f"❌ Error getting word frequencies: {e}")


def predict_next_word(ngrams_obj):
    print("\n=== NEXT WORD PREDICTION ===")
    
    prefix = prompt("Enter a phrase (e.g., 'Alice was'): ")
    if not validate_input(prefix):
        print("❌ Please enter some text!")
        return
    
    try:
        suggestions = ngrams_obj.suggest_next(prefix, top_k=5, use_smoothing=False)
        
        if not suggestions:
            print(f"❌ No predictions found for '{prefix}'")
            print("Try a different phrase or check your spelling.")
            return
        
        print(f"\n🎯 Possible next words after '{prefix}':")
        
        filtered_suggestions = [(word, freq) for word, freq in suggestions 
                              if word not in ["<START>", "<END>"]]
        
        if filtered_suggestions:
            table = format_frequency_table(filtered_suggestions, f"Next Words After '{prefix}'")
            print(table)
        else:
            print("No valid word predictions found.")
            
    except Exception as e:
        print(f"❌ Error predicting next word: {e}")


def show_all_next_words(ngrams_obj):
    print("\n=== ALL POSSIBLE NEXT WORDS ===")
    
    prefix = prompt("Enter a phrase (e.g., 'the'): ")
    if not validate_input(prefix):
        print("❌ Please enter some text!")
        return
    
    try:
        context_freqs = ngrams_obj.get_context_frequencies(prefix)
        
        if not context_freqs:
            print(f"❌ No words found after '{prefix}'")
            print("Try a different phrase or check your spelling.")
            return
        
        print(f"\n📝 All possible words after '{prefix}':")
        table = format_frequency_table(context_freqs, f"All Next Words After '{prefix}'")
        print(table)
        
    except Exception as e:
        print(f"❌ Error getting context frequencies: {e}")


def show_model_statistics(ngrams_obj):
    print("\n=== MODEL STATISTICS ===")
    
    try:
        stats = ngrams_obj.get_model_stats()
        
        print(f"📊 N-Gram Model Statistics:")
        print(f"   • N-gram order: {stats['n_gram_order']}")
        print(f"   • Total tokens: {stats['total_tokens']:,}")
        print(f"   • Unique words: {stats['unique_words']:,}")
        print(f"   • Vocabulary size: {stats['vocabulary_size']:,}")
        print(f"   • Contexts: {stats['contexts']:,}")
        
        print(f"\n🏆 Top 5 Most Common Words:")
        for i, (word, freq) in enumerate(stats['most_common_words'], 1):
            print(f"   {i}. '{word}' (frequency: {freq})")
            
    except Exception as e:
        print(f"❌ Error getting model statistics: {e}")


if __name__ == "__main__":
    demo_word_frequencies()
