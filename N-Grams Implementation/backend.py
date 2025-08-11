import json
import random
import time
import re
import csv
import os
from collections import defaultdict

class NGramModel:
    def __init__(self, n=3):
        self.n = n
        self.ngrams = defaultdict(list)
        self.corpus = []
        self.word_frequencies = defaultdict(int)
        
    def load_corpus_from_csv(self, file_path):
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if row:
                            text = ' '.join(row)
                            self.add_text_to_corpus(text)
                print(f"Loaded corpus from {file_path}")
            else:
                print(f"Corpus file {file_path} not found, using default texts")
                self.load_default_corpus()
        except Exception as e:
            print(f"Error loading corpus: {e}")
            self.load_default_corpus()
    
    def add_text_to_corpus(self, text):
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        self.corpus.extend(words)
        
        for word in words:
            self.word_frequencies[word] += 1
    
    def load_default_corpus(self):
        default_texts = [
            "The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet at least once.",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell.",
            "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness.",
            "To be or not to be, that is the question. Whether tis nobler in the mind to suffer the slings and arrows of outrageous fortune.",
            "Artificial intelligence revolution transforms how we interact with technology daily. Machine learning algorithms process vast amounts of data.",
            "Natural language processing enables computers to understand human language patterns. Deep learning models analyze text structure.",
            "Computational linguistics combines computer science with linguistic theory. Statistical methods help identify language patterns.",
            "Text generation using n-grams creates realistic language models. Probability distributions determine word sequences.",
            "Corpus analysis reveals language usage patterns and frequency distributions. Statistical analysis helps understand linguistic phenomena."
        ]
        
        for text in default_texts:
            self.add_text_to_corpus(text)
    
    def build_ngrams(self):
        if len(self.corpus) < self.n:
            print("Corpus too small for n-gram model")
            return
        
        for i in range(len(self.corpus) - self.n + 1):
            ngram = tuple(self.corpus[i:i + self.n - 1])
            next_word = self.corpus[i + self.n - 1]
            self.ngrams[ngram].append(next_word)
        
        print(f"Built {len(self.ngrams)} n-grams from corpus")
    
    def generate_text(self, length=50, start_words=None):
        if not self.ngrams:
            self.build_ngrams()
        
        if not self.ngrams:
            return self.generate_random_text(length)
        
        if start_words and len(start_words) >= self.n - 1:
            current = tuple(start_words[-(self.n-1):])
        else:
            current = random.choice(list(self.ngrams.keys()))
        
        generated_words = list(current)
        
        for _ in range(length - len(generated_words)):
            if current in self.ngrams:
                next_word = random.choice(self.ngrams[current])
                generated_words.append(next_word)
                current = tuple(generated_words[-(self.n-1):])
            else:
                if self.corpus:
                    next_word = random.choice(self.corpus)
                    generated_words.append(next_word)
                    current = tuple(generated_words[-(self.n-1):])
                else:
                    break
        
        return ' '.join(generated_words)
    
    def generate_random_text(self, length=50):
        if not self.corpus:
            return "The quick brown fox jumps over the lazy dog."
        
        selected_words = random.choices(self.corpus, k=min(length, len(self.corpus)))
        return ' '.join(selected_words)
    
    def get_corpus_stats(self):
        return {
            'total_words': len(self.corpus),
            'unique_words': len(self.word_frequencies),
            'ngram_count': len(self.ngrams),
            'most_common_words': sorted(self.word_frequencies.items(), key=lambda x: x[1], reverse=True)[:10]
        }

class TypingTest:
    def __init__(self):
        self.ngram_model = NGramModel(n=3)
        self.corpus_path = "corpora/words_pos.csv"
        self.load_corpus()
        
    def load_corpus(self):
        self.ngram_model.load_corpus_from_csv(self.corpus_path)
    
    def get_random_text(self, use_ngrams=True, length=30):
        if use_ngrams and self.ngram_model.ngrams:
            return self.ngram_model.generate_text(length)
        else:
            return self.ngram_model.generate_random_text(length)
    
    def get_multiple_texts(self, count=5, use_ngrams=True, length=30):
        texts = []
        for _ in range(count):
            texts.append(self.get_random_text(use_ngrams, length))
        return texts
    
    def calculate_wpm(self, typed_text, time_taken):
        if time_taken <= 0:
            return 0
        
        word_count = len(typed_text.strip().split())
        minutes = time_taken / 60
        return round(word_count / minutes)
    
    def calculate_accuracy(self, original_text, typed_text):
        original_words = original_text.strip().split()
        typed_words = typed_text.strip().split()
        
        if not original_words:
            return 100
        
        correct_words = 0
        min_length = min(len(original_words), len(typed_words))
        
        for i in range(min_length):
            if original_words[i] == typed_words[i]:
                correct_words += 1
        
        accuracy = (correct_words / len(original_words)) * 100
        return round(accuracy)
    
    def get_test_results(self, original_text, typed_text, time_taken):
        wpm = self.calculate_wpm(typed_text, time_taken)
        accuracy = self.calculate_accuracy(original_text, typed_text)
        
        original_words = original_text.strip().split()
        typed_words = typed_text.strip().split()
        
        word_analysis = []
        min_length = min(len(original_words), len(typed_words))
        
        for i in range(min_length):
            is_correct = original_words[i] == typed_words[i]
            word_analysis.append({
                'position': i,
                'original': original_words[i],
                'typed': typed_words[i],
                'correct': is_correct
            })
        
        extra_words = typed_words[min_length:] if len(typed_words) > min_length else []
        
        return {
            'wpm': wpm,
            'accuracy': accuracy,
            'time_taken': round(time_taken, 2),
            'word_count': len(typed_words),
            'char_count': len(typed_text),
            'word_analysis': word_analysis,
            'extra_words': extra_words,
            'corpus_stats': self.ngram_model.get_corpus_stats()
        }

typing_test = TypingTest()

def get_test_text(use_ngrams=True, length=30):
    return typing_test.get_random_text(use_ngrams, length)

def get_multiple_texts(count=5, use_ngrams=True, length=30):
    return typing_test.get_multiple_texts(count, use_ngrams, length)

def submit_test_results(original_text, typed_text, time_taken):
    return typing_test.get_test_results(original_text, typed_text, time_taken)

def get_corpus_stats():
    return typing_test.ngram_model.get_corpus_stats()

if __name__ == "__main__":
    print("Testing N-Grams Backend...")
    print("=" * 40)
    
    print("Corpus Statistics:")
    stats = typing_test.ngram_model.get_corpus_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 40)
    
    print("Generated Text (N-grams):")
    text1 = typing_test.get_random_text(use_ngrams=True, length=20)
    print(text1)
    
    print("\nGenerated Text (Random):")
    text2 = typing_test.get_random_text(use_ngrams=False, length=20)
    print(text2)
    
    print("\n" + "=" * 40)
    
    print("Multiple Texts for Continuous Typing:")
    texts = typing_test.get_multiple_texts(count=3, use_ngrams=True, length=15)
    for i, text in enumerate(texts, 1):
        print(f"Text {i}: {text}")
    
    print("\n" + "=" * 40)
    print("Backend test completed successfully!") 