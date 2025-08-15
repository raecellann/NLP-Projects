# WPM Typing Test - Orangutype 🐒⌨️

 Python desktop application using pygame that measures WPM with N-grams corpus-based text generation. Uses `corpora/eng_sentences.txt`.

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

## N-Grams Implementation

- **Corpus Loading**: Reads from `corpora/eng_sentences.txt` (one sentence per line)
- **N-gram Building**: Creates tri-gram mappings and next-word distributions
- **Text Generation**: Generates coherent text with fallback to random words

### Prerequisites

- Python (v3.8 or higher)
- pip

### Installation

1. Navigate to the project directory:

```bash
cd "MIDTERM"
cd "Activity 1"
cd "yesh-ngrams"
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

- UI colors and layout (should improve) (header, time buttons, live stats, text area, results panel).
- Input field shows "Start here" placeholder and has a blinking cursor when active. (this part is optional)
- User profile is recommended. Where the user may able to see his/her progress. This may also use to track the improvements of user's wpm. 