from command import *

if __name__ == "__main__":
    ClearScreen().execute()
    print("🐸 Jejemon Translator CLI 🐸\n")
    data = LoadData("data/jejemon.json").execute()
    TranslatorLoop(data).execute()
