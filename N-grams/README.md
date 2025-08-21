## N-Grams Typing Challenge

A modern typing test that generates practice text using N-gram language models with difficulty levels. Built with Python and Pygame.

### Features
- **N-gram generator**: Easy, Medium, Hard word selections from `corpora/corpora.pkl`
- **Modern UI**: Animated buttons, gradient background, particle effects
- **Typing metrics**: WPM, accuracy, progress bar, results screen
- **Flexible timing**: 15/30/60/120 seconds
- **CLI and GUI**: Use the console menu or launch the typing game directly

### Requirements
- Python 3.9+
- Pygame

Install dependencies:
```bash
pip install pygame
```

### Quick Start
- Run the interactive console menu (recommended):
```bash
python main.py
```

- Launch the typing game directly:
```bash
python typing_test.py
```

- Or launch programmatically:
```python
from typing_test import run_typing_test_with_ngrams

run_typing_test_with_ngrams(difficulty="medium", time_limit=60)
```

### Project Structure
```text
N-grams/
  corpora/
    corpora.pkl            # Pickled corpus with easy/medium/hard sections
    eng_sentences.txt      # (Optional) raw text sources
    long-texts.txt
    medium-texts.txt
    short-texts.txt
  multimedia/
    bg.png                 # Menu background
  typing_game/             # Refactored game modules (OOP)
    __init__.py
    constants.py           # Sizes, colors, states
    particles.py           # Particle effect
    ui.py                  # Buttons and UI widgets
    game.py                # TypingGame class (main logic)
  ngrams.py                # N-gram model and helpers
  typing_test.py           # Entry point for GUI; keeps a public wrapper function
  main.py                  # Console menu that can launch the GUI
  README.md
```

### Notes on Refactor
- The original large `typing_test.py` has been split into the `typing_game` package for clarity and maintainability.
- `typing_test.py` remains as a thin entry point exposing `run_typing_test_with_ngrams(...)` for backward compatibility.

### Corpora
- The app expects `corpora/corpora.pkl` to exist. It can be a dictionary with keys like `easy`, `medium`, `hard` (case-insensitive, aliases supported). Each value can be a list of words/phrases or a multi-line string.

### Troubleshooting
- If Pygame fails to initialize sound, the game will still run (sound is optional).
- On Windows, if you see a blank window, update graphics drivers and ensure `pip install pygame` succeeded.
- If `corpora/corpora.pkl` is missing, phrase generation falls back gracefully but results may be limited.

### License
No license specified. Add one if you plan to distribute.


