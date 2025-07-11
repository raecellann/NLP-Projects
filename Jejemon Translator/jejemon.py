from translator import JejemonTranslator

class JejemonZ:
    def __init__(self):
        self.translator = JejemonTranslator()

    def run(self):
        print("Welcome Stupid Hooman, here comes your jejemon translator ⸜(｡˃ ᵕ < )⸝♡")
        try:
            while True:
                print("\nChoose an option:")
                print("1. Normal text to Jejemon")
                print("2. Jejemon to Normal text")
                print("3. Exit")
                choice = input("> ").strip()
                if choice == "3":
                    print("Program Finished.")
                    break
                elif choice == "1":
                    while True:
                        try:
                            user_input = input("Enter normal text (or type 'back' to return to menu): ")
                            if user_input.strip().lower() == 'back':
                                break
                            normalized = self.translator.normalize(user_input)
                            jejemonized = self.translator.jejemonize(normalized)
                            emotion = self.translator.detect_emotion(user_input)
                            emoji = self.translator.get_emoji(emotion)
                            print(f"👾 Jejemon: {jejemonized}\n🧠 Emotion Detected: {emoji} {emotion.capitalize()}")
                        except KeyboardInterrupt:
                            print("\n\nReturning to main menu...")
                            break
                elif choice == "2":
                    while True:
                        try:
                            user_input = input("Enter jejemon text (or type 'back' to return to menu): ")
                            if user_input.strip().lower() == 'back':
                                break
                            normalized = self.translator.normalize(user_input)
                            emotion = self.translator.detect_emotion(user_input)
                            emoji = self.translator.get_emoji(emotion)
                            print(f"📝 Normalized: {normalized}\n🧠 Emotion Detected: {emoji} {emotion.capitalize()}")
                        except KeyboardInterrupt:
                            print("\n\nReturning to main menu...")
                            break
                else:
                    print("Invalid choice. Please select 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\nBye Bitch!👋") 