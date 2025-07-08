import re
import json
import os
import random

class Command:
    def execute(self):
        pass

class ClearScreen(Command):
    def execute(self):
        os.system('cls' if os.name == 'nt' else 'clear')

class LoadData(Command):
    def __init__(self, file_path):
        self.file_path = file_path

    def execute(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

class TranslateText(Command):
    def __init__(self, text, data):
        self.text = text
        self.data = data

    def simple_sentiment(self, text):
        positive_words = ["love", "happy", "good", "great", "amazing", "awesome", "like", "enjoy", "fun", "nice", "best", "fantastic", "wonderful", "smile"]
        negative_words = ["sad", "bad", "hate", "angry", "terrible", "awful", "worst", "cry", "pain", "problem", "sucks", "dislike", "annoy", "upset"]
        text_lower = text.lower()
        pos = sum(word in text_lower for word in positive_words)
        neg = sum(word in text_lower for word in negative_words)
        if pos > neg:
            return "positive"
        elif neg > pos:
            return "negative"
        else:
            return "neutral"

    def get_sentiment_emoticons(self, sentiment, emoticons_map):
        if sentiment == "positive":
            return {
                ":-)": "😊", ":-(": "😢", ";-)": "😉", ":-P": "😛",
                "XD": "😂", ":3": "😺", ":D": "😁", ":O": "😮",
                ":'(": "😭", ":|": "😐", ":/": "😕", ":P": "😜",
                ":)": "🙂", ":(": "🙁"
            }
        elif sentiment == "negative":
            return {
                ":-)": "😔", ":-(": "😢", ";-)": "😔", ":-P": "😔",
                "XD": "😔", ":3": "😔", ":D": "😔", ":O": "😔",
                ":'(": "😭", ":|": "😔", ":/": "😔", ":P": "😔",
                ":)": "😔", ":(": "😢"
            }
        else:
            return emoticons_map

    def execute(self):
        chars_map = self.data["chars"]
        emoticons_map = self.data.get("emoticons", {})
        known_words = {
            "ako": ["aq", "4k0", "akuh"],
            "ikaw": ["ik4w", "ekaw", "ykaw"],
            "na": ["n4", "nuh"],
            "po": ["ph0w", "pf0w"],
            "kamusta": ["muztah", "uztah", "kumuztah"],
            "mahal": ["mHaL", "m4h4L"],
            "kita": ["kiT4", "qta"],
            "love": ["lAbqCkyOuHh", "l0v3"],
            "hello": ["eEoWpFhUeEhsxz", "heLLoWh"],
            "you": ["yuhh", "yu", "u"]
        }

        sentiment = self.simple_sentiment(self.text)
        sentiment_emoticons = self.get_sentiment_emoticons(sentiment, emoticons_map)

        emoticon_patterns = sorted(map(re.escape, emoticons_map.keys()), key=len, reverse=True)
        emoticon_regex = "|".join(emoticon_patterns)

        pattern = rf"({emoticon_regex})|(\w+)|(\W+)"
        tokens = re.findall(pattern, self.text)
        result = []
        for match in tokens:
            emoticon, word, nonword = match
            if emoticon:
                result.append(sentiment_emoticons.get(emoticon, emoticon))
            elif word:
                lower_token = word.lower()

                if lower_token in known_words:
                    result.append(random.choice(known_words[lower_token]))
                else:

                    converted = ""
                    for char in word:
                        lower_char = char.lower()
                        if lower_char in chars_map:
                            replacement = random.choice(chars_map[lower_char])
                            replacement = replacement.upper() if char.isupper() else replacement
                            converted += replacement
                        else:
                            converted += char
                    result.append(converted)
            elif nonword:
                result.append(nonword)
        jejemon_output = ''.join(result)
        print("\nJejemon Output:\n")
        print(jejemon_output)
        print()
        return jejemon_output

class TranslatorLoop(Command):
    def __init__(self, data):
        self.data = data

    def execute(self):
        running = True
        while running:
            user_input = input("Enter text (or type 'exit'): ")
            if user_input.lower() == 'exit':
                running = False
            else:
                TranslateText(user_input, self.data).execute()
