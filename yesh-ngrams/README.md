# WPM Typing Test - N-Grams Implementation (pygame)

Pure Python desktop application using pygame that measures WPM with N-grams corpus-based text generation. Uses `corpora/eng_sentences.txt`.

## Features

- **Real-time WPM calculation** with live statistics
- **N-grams implementation** (tri-grams) for text generation
- **Configurable test duration** (15s, 30s, 60s, 120s)
- **Accuracy measurement** with word-by-word comparison and highlighting
- **Live progress tracking** with countdown timer
- **Results panel** with WPM, Accuracy, Time, and Words
- **Interactive input field** with "Start here" placeholder and blinking cursor
- **Resizable window** with responsive layout

## Project Structure

```
N-Grams Implementation/
├── main.py              # Main application orchestrator
├── gui.py               # GUI components (Button, InputField, TypingInterface)
├── typing_logic.py      # Typing test logic and state management
├── backend.py           # N-gram model and typing metrics
├── corpora/
│   └── eng_sentences.txt
└── README.md
```

## Technology Stack

- **UI**: pygame (no web stack)
- **Logic**: Python (pure implementation, no external libraries besides pygame)
- **Architecture**: Modular OOP design with separation of concerns

## N-Grams Implementation

- **Corpus Loading**: Reads from `corpora/eng_sentences.txt` (one sentence per line)
- **N-gram Building**: Creates tri-gram mappings and next-word distributions
- **Text Generation**: Generates coherent text with fallback to random words

## Setup Instructions

### Prerequisites

- Python (v3.8 or higher)
- pip

### Installation

1. Navigate to the project directory:

```bash
cd "N-Grams Implementation"
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

## Usage

1. Pick a test duration from the top buttons (15/30/60/120).
2. Click on the input field (shows "Start here" placeholder) and start typing; the test starts on first keystroke.
3. Watch live stats (time, WPM, accuracy) update in real time.
4. When time ends, view results. Use "New Test" or "Reset" to continue.

## Python Backend Features

The `backend.py` file contains:

- **NGramModel**: Implements tri-gram text generation
- **TypingTest**: Provides random text generation, WPM and accuracy calculations
- **Corpus Management**: Loads from `corpora/eng_sentences.txt` with fallbacks

## Notes

- UI colors and layout mimic the original web version (header, time buttons, live stats, text area, results panel).
- Keyboard shortcut: Ctrl+Shift+Enter to start a new test.
- Input field shows "Start here" placeholder and has a blinking cursor when active.
- Window is resizable with responsive layout that adapts to different screen sizes.
