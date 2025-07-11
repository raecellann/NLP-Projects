import re
import json
import os
import random

class Tokenizer:
    def __init__(self):
        emoticons = r"[:;=8][\-o\*']?[\)\]dDpP(/\\|\[@]"
        self.pattern = re.compile(
            rf"(?:{emoticons})|\w+|[^\w\s]|\s+",
            re.IGNORECASE
        )

    def tokenize(self, text):
        return self.pattern.findall(text)


class JejemonNormalizer:
    def __init__(self):
        data_path = os.path.join(os.path.dirname(__file__), 'data.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.word_map = data["word_map"]

        flat_char_map = {}
        for letter, replacements in data["char_map"].items():
            for replacement in replacements:
                flat_char_map[replacement] = letter

        # Remove str.maketrans and store flat_char_map for custom replacement
        self.char_map = flat_char_map
        self.reverse_word_map = {v: k for k, v in self.word_map.items()}

        self.reverse_char_map = {}
        for letter, replacements in data["char_map"].items():
            for replacement in replacements:
                self.reverse_char_map[letter] = replacement

        self.original_char_map = data["char_map"]

    def preserve_casing(self, original, converted):
        if original.isupper():
            return converted.upper()
        elif original[0].isupper():
            return converted.capitalize()
        return converted

    def normalize_token(self, token):
        if token.strip() == "":
            return token

        lowered = token.lower()

        if len(lowered) <= 2 and lowered not in self.word_map:
            return self.preserve_casing(token, self._multi_replace(lowered, self.char_map))

        norm = self.word_map.get(lowered)
        if not norm:
            corrected, dist = find_closest_word(lowered, self.word_map.keys(), max_distance=1)
            if corrected:
                print(f"[Auto-correct] '{lowered}' → '{corrected}'")
                norm = self.word_map[corrected]
            else:
                norm = self._multi_replace(lowered, self.char_map)

        return self.preserve_casing(token, norm)

    def _multi_replace(self, text, replace_map):
        # Sort keys by length (desc) to handle multi-char replacements first
        for key in sorted(replace_map, key=len, reverse=True):
            text = text.replace(key, replace_map[key])
        return text

    def jejemonize_token(self, token, seed=None):
        if token.strip() == "":
            return token

        if seed is not None:
            random.seed(seed)

        lowered = token.lower()
        jej = self.reverse_word_map.get(lowered)

        if jej:
            result = jej
        else:
            result = ""
            for c in lowered:
                if c in self.original_char_map:
                    replacements = self.original_char_map[c]
                    result += random.choice(replacements)
                else:
                    result += c

        return self.preserve_casing(token, result)

    def jejemonize(self, text, tokenizer=None, seed=None):
        if tokenizer is None:
            tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(text)
        jej_tokens = [self.jejemonize_token(tok, seed=seed) for tok in tokens]
        return "".join(jej_tokens)


class TokenEmotionClassifier:
    def __init__(self):
        data_path = os.path.join(os.path.dirname(__file__), 'data.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.emotion_keywords = {k: set(v) for k, v in data["emotion_keywords"].items()}
        self.emoticon_map = data["emoticon_map"]

    def classify(self, tokens):
        scores = {emotion: 0 for emotion in self.emotion_keywords}
        for token in tokens:
            word = token.lower()
            if word in self.emoticon_map:
                scores[self.emoticon_map[word]] += 2
                continue
            for emotion, keywords in self.emotion_keywords.items():
                if word in keywords:
                    scores[emotion] += 1
        top_emotion = max(scores, key=lambda k: scores[k])
        return top_emotion if scores[top_emotion] > 0 else "neutral"

    def emoji(self, emotion):
        return {
            "joy": "😊", "anger": "😡", "sadness": "😢",
            "fear": "😱", "surprise": "😲", "disgust": "🤢", "neutral": "😐"
        }.get(emotion, "😐")


def edit_distance(s1, s2):
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def find_closest_word(word, word_list, max_distance=1):
    closest_word = None
    closest_distance = None
    for candidate in word_list:
        dist = edit_distance(word, candidate)
        if closest_distance is None or dist < closest_distance:
            closest_word = candidate
            closest_distance = dist
    if closest_distance is not None and closest_distance <= max_distance:
        return closest_word, closest_distance
    return None, None
