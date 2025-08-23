## N-Grams Typing Challenge

A modern typing test that generates practice text using N-gram language models with difficulty levels. Built with Python and Pygame.

### Features
- **N-gram generator**: Easy, Medium, Hard word selections from `corpora/corpora.pkl`
- **Modern UI**: Animated buttons, gradient background, particle effects
- **Typing metrics**: WPM, accuracy, progress bar, results screen
- **Flexible timing**: 15/30/60/120 seconds
- **CLI and GUI**: Use the console menu or launch the typing game directly
- **📊 Progress Tracking**: Automatic data collection and detailed statistics

### Requirements
- Python 3.9+
- Pygame

Install dependencies:
```bash
pip install pygame
```

### Quick Start
- Run the interactive console menu:
```bash
python main.py
```

- Launch the typing game directly:
```bash
python typing_test.py
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
    bg.png                
  typing_game/             
    __init__.py
    constants.py           # Sizes, colors, states
    particles.py           # Particle effect
    ui.py                  # Buttons and UI widgets
    game.py                # TypingGame class (main logic)
  progress_tracker/        # 📊 Progress tracking system
    __init__.py           # Package initialization
    tracker.py            # Core tracking functionality
    dashboard.py          # Progress dashboard
    test.py               # Package testing
    README.md             # Package documentation
  ngrams.py                # N-gram model and helpers
  typing_test.py           # Entry point for GUI; keeps a public wrapper function
  main.py                  # Console menu that can launch the GUI
  README.md
```

### 📊 Progress Tracking Features

- **Automatic Data Collection**: Every typing test result is automatically saved
- **Simplified Numbers**: WPM and accuracy rounded to 1 decimal place (e.g., 63.2 instead of 63.23529411764706)
- **Simple Dates**: YYYY-MM-DD format (e.g., 2025-08-23)
- **Single File Storage**: Clean `typing_progress.json` without backup complexity
- **Progress Dashboard**: Interactive dashboard with detailed statistics
- **Difficulty Analysis**: Performance breakdown by difficulty level
- **Data Export**: Export to CSV or JSON for external analysis


