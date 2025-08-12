import re
from typing import List


def tokenize(text: str, special_tokens: bool = True) -> List[str]:
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


def print_menu(title: str, options: List[str]) -> None:
    print(f"\n--- {title} ---")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")


def prompt(message: str) -> str:
    return input(message)


def format_frequency_table(word_freqs: List[tuple], title: str = "Word Frequencies") -> str:
    if not word_freqs:
        return f"{title}\nNo data available."
        
    max_word_len = max(len(word) for word, _ in word_freqs)
    
    table = f"\n=== {title} ===\n"
    table += f"{'Word':<{max_word_len + 2}} {'Frequency':<12} {'Percentage':<12}\n"
    table += "-" * (max_word_len + 30) + "\n"
    
    total_freq = sum(freq for _, freq in word_freqs)
    
    for word, freq in word_freqs:
        percentage = (freq / total_freq) * 100 if total_freq > 0 else 0
        table += f"{word:<{max_word_len + 2}} {freq:<12} {percentage:.1f}%\n"
        
    table += f"\nTotal frequency: {total_freq}"
    return table


def validate_input(text: str, min_length: int = 1) -> bool:
    return text and text.strip() and len(text.strip()) >= min_length
