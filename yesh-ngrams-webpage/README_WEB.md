# ORANGUTYPE - Web Version

A retro-styled typing test application with HTML/CSS frontend and Python backend, featuring N-gram text generation.

## Features

- 🎯 **Retro Pixelated Design** - Dark theme with neon blue/purple accents
- ⌨️ **Real-time Typing Test** - Test your typing speed and accuracy
- 🧠 **N-gram Text Generation** - AI-powered text using machine learning
- ⏱️ **Multiple Test Durations** - 15, 30, 60, or 120 seconds
- 📊 **Live Statistics** - WPM, accuracy, and time tracking
- 🌐 **Web-based Interface** - No installation required, works in any browser

## Quick Start

### Option 1: Simple Launcher (Recommended)
```bash
python run_web.py
```
This will automatically:
- Start the web server
- Open your default browser
- Navigate to the application

### Option 2: Manual Server Start
```bash
python web_server.py
```
Then manually open your browser and go to: `http://localhost:8000`

## How to Use

1. **Start a Test**: Click on the text area or press any key
2. **Type the Words**: Type each word and press space to continue
3. **View Results**: See your WPM, accuracy, and time when the test completes
4. **Customize Settings**: 
   - Choose test duration (15, 30, 60, 120 seconds)
   - Toggle punctuation and numbers
   - Start new tests or restart current ones

## Keyboard Shortcuts

- **Tab + Shift**: Restart current test
- **Ctrl + Shift + Enter**: Start new test
- **Space**: Submit word and continue

## File Structure

```
yesh-ngrams/
├── index.html          # Main HTML interface
├── style.css           # Retro pixelated styling
├── web_server.py       # Python HTTP server
├── run_web.py          # Easy launcher script
├── backend.py          # N-gram text generation
├── typing_logic.py     # Typing test logic
├── corpora/            # Text corpus for training
└── README_WEB.md       # This file
```

## Technical Details

- **Frontend**: Pure HTML/CSS with vanilla JavaScript
- **Backend**: Python HTTP server using built-in modules
- **Text Generation**: N-gram language model (3-grams)
- **No Dependencies**: Uses only Python standard library
- **Cross-platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.6 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No additional packages required

## Troubleshooting

### Port Already in Use
If you get a "port already in use" error:
1. Stop any other servers running on port 8000
2. Or modify the port in `web_server.py`

### Browser Not Opening
If the browser doesn't open automatically:
1. Manually navigate to `http://localhost:8000`
2. Check if your default browser is properly configured

### Text Not Loading
If no text appears:
1. Check that `corpora/eng_sentences.txt` exists
2. Ensure all Python files are in the same directory

## Customization

### Changing Colors
Edit `style.css` and modify the CSS variables:
```css
:root {
    --bg-color: #202020;        /* Background color */
    --accent-blue: #00bfff;     /* Blue accent */
    --accent-purple: #8a2be2;   /* Purple accent */
}
```

### Adding New Text
Place your text files in the `corpora/` folder:
- `.txt` files for plain text
- `.csv` files for structured data

### Modifying Test Duration
Edit the time options in `index.html`:
```html
<span class="time-option" data-duration="15">15</span>
<span class="time-option" data-duration="30">30</span>
```

## Development

To modify the application:
1. Edit `index.html` for UI changes
2. Edit `style.css` for styling
3. Edit `web_server.py` for backend logic
4. Edit `typing_logic.py` for typing mechanics

## License

This project is open source and available under the same license as the original yesh-ngrams project.

---

**Enjoy improving your typing skills with ORANGUTYPE!** 🚀
