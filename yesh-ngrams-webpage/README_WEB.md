# ORANGUTYPE - Web Version

Retro-styled typing test served as a static site. A tiny Python server preloads corpora from `corpora/*.txt`, caches them with pickle, and emits a `corpora.js` file consumed by the frontend (no Flask, no API).

## Features

- 🎯 **Retro Pixelated Design** - Dark theme with neon blue/purple accents
- ⌨️ **Real-time Typing Test** - Test your typing speed and accuracy
- 🧠 **N-gram Text Generation** - AI-powered text using machine learning
- ⏱️ **Multiple Test Durations** - 15, 30, 60, or 120 seconds
- 📊 **Live Statistics** - WPM, accuracy, and time tracking
- 🌐 **Web-based Interface** - No installation required, works in any browser

## Quick Start

### Run
```bash
python server.py
```
This will build the corpora cache and open `http://localhost:8000`.

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
yesh-ngrams-webpage/
├── index.html          # Landing page with difficulty buttons
├── test.html           # Typing UI, reads corpora from corpora.js
├── style.css           # Styling
├── server.py           # Static server + pickle cache builder
├── backend.py          # N-gram utilities (desktop/legacy)
├── typing_logic.py     # Desktop/legacy logic
├── corpora/            # short/medium/long text files and corpora.pkl
└── README_WEB.md
```

## Technical Details

- **Frontend**: Pure HTML/CSS with vanilla JavaScript
- **Backend**: Python static server using only built-in modules
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
2. Or run `python server.py 8001`

### Browser Not Opening
If the browser doesn't open automatically:
1. Manually navigate to `http://localhost:8000`
2. Check if your default browser is properly configured

### Text Not Loading
If no text appears:
1. Ensure `corpora/short-texts.txt`, `medium-texts.txt`, and `long-texts.txt` exist
2. Delete `corpora/corpora.pkl` to force a rebuild, then rerun `python server.py`

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
Edit the time options in `test.html`:
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
