# N-Grams Typing Test Application

A modern, modular typing test application that uses N-gram language models to generate text with different difficulty levels. Built with Python and Pygame, featuring a beautiful UI with particle effects and smooth animations.

## 🏗️ Project Architecture

The application has been refactored to be fully modular and object-oriented:

### Core Modules

- **`constants.py`** - Centralized configuration, colors, and game settings
- **`ui_components.py`** - Button classes and UI elements (ModernButton, OutlineButton, ButtonFactory)
- **`game_states.py`** - Game screen states (MenuState, PlayGameState, ResultsState)
- **`game_logic.py`** - Core game mechanics and logic separate from UI
- **`particles.py`** - Particle system for visual effects
- **`game_controller.py`** - Main controller that orchestrates all components
- **`ngrams.py`** - N-gram language model implementation
- **`main.py`** - Command-line interface for text generation

### Design Patterns Used

- **State Pattern** - Different game screens as separate state classes
- **Factory Pattern** - Button creation through ButtonFactory
- **Observer Pattern** - Game states observe the game controller
- **Separation of Concerns** - UI, logic, and data are completely separated

## 🚀 How to Run

### Prerequisites

1. **Python 3.7+** installed on your system
2. **Pygame** library installed

### Installation

1. **Install Pygame:**
   ```bash
   pip install pygame
   ```

2. **Navigate to the N-grams directory:**
   ```bash
   cd "N-grams"
   ```

### Running the Application

#### Option 1: Typing Test Game (Recommended)
```bash
python game_controller.py
```
This launches the full graphical typing test with:
- Beautiful animated menu
- Three difficulty levels (Easy, Medium, Hard)
- Configurable time limits (15s, 30s, 60s, 120s)
- Real-time accuracy and WPM tracking
- Particle effects and smooth animations

#### Option 2: Command-Line Interface
```bash
python main.py
```
This provides a text-based interface for:
- Generating text phrases with different difficulty levels
- Viewing difficulty statistics
- Verifying corpora integrity
- Launching the typing test

#### Option 3: Direct N-gram Usage
```bash
python -c "
from ngrams import Ngrams
ng = Ngrams(n=3, num_phrases=5, difficulty='medium')
print(ng.generate_phrases())
"
```

## 🎮 Game Features

### Difficulty Levels
- **Easy**: 2-gram model, short words (3-4 letters), basic vocabulary
- **Medium**: 3-gram model, medium words (5-7 letters), moderate vocabulary  
- **Hard**: 4-gram model, long words (8+ letters), complex vocabulary

### Time Limits
- **15 seconds** - Quick warm-up
- **30 seconds** - Short practice session
- **60 seconds** - Standard test duration
- **120 seconds** - Extended practice

### Visual Features
- **Animated backgrounds** with gradient effects
- **Particle systems** for feedback and ambiance
- **Smooth button animations** with hover effects
- **Real-time progress tracking** with visual progress bars
- **Modern UI design** with glass-morphism effects

## 📁 File Structure

```
N-grams/
├── README.md                 # This file
├── constants.py              # Game constants and configuration
├── ui_components.py          # Button and UI component classes
├── game_states.py            # Game screen state classes
├── game_logic.py             # Core game mechanics
├── particles.py              # Particle system for effects
├── game_controller.py        # Main game controller
├── ngrams.py                 # N-gram language model
├── main.py                   # Command-line interface
├── corpora/                  # Text corpora directory
│   ├── corpora.pkl          # Main corpus file
│   ├── eng_sentences.txt    # English sentences
│   ├── long-texts.txt       # Long text samples
│   ├── medium-texts.txt     # Medium text samples
│   └── short-texts.txt      # Short text samples
└── multimedia/               # Game assets
    └── bg.png               # Background image
```

## 🔧 Configuration

### Customizing Game Settings

Edit `constants.py` to modify:
- Window dimensions
- Color schemes
- Difficulty parameters
- Time limits
- UI spacing and dimensions

### Adding New Difficulty Levels

1. Add new settings to `DIFFICULTY_SETTINGS` in `constants.py`
2. Update the button creation in `ButtonFactory.create_menu_buttons()`
3. Add corresponding logic in `MenuState.handle_event()`

### Modifying UI Components

- **Buttons**: Extend `ModernButton` or `OutlineButton` classes
- **Layouts**: Modify positioning in `ButtonFactory` methods
- **Effects**: Customize particle systems in `particles.py`

## 🧪 Testing and Development

### Running Tests
```bash
# Test N-gram generation
python -c "from ngrams import Ngrams; print(Ngrams().generate_phrases())"

# Test UI components
python -c "from ui_components import ModernButton; print('UI components loaded successfully')"

# Test game logic
python -c "from game_logic import GameLogic; print('Game logic loaded successfully')"
```

### Debug Mode
Add debug prints in any module:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🐛 Troubleshooting

### Common Issues

1. **"pygame module not found"**
   - Install pygame: `pip install pygame`

2. **"corpora/corpora.pkl not found"**
   - Ensure the corpora directory exists with the required files
   - Check file permissions

3. **"Error loading menu background"**
   - The game will use animated backgrounds instead
   - Check if `multimedia/bg.png` exists

4. **Performance issues**
   - Reduce particle count in `particles.py`
   - Lower FPS in `constants.py`

### Performance Optimization

- **Particles**: Adjust `generate_background_particles()` count
- **FPS**: Modify `FPS` constant in `constants.py`
- **Window size**: Reduce dimensions for better performance on slower systems

## 🤝 Contributing

### Adding New Features

1. **New Game States**: Extend `GameState` base class
2. **New UI Components**: Add to `ui_components.py`
3. **New Game Logic**: Extend `GameLogic` class
4. **New Effects**: Enhance `ParticleSystem` class

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters
- Add docstrings to all classes and methods
- Keep modules focused on single responsibilities

## 📚 Technical Details

### N-Gram Model
- Supports 2-5 gram orders
- Interpolation-based probability calculation
- Difficulty-based word filtering
- Automatic text generation with fallbacks

### Game Engine
- 60 FPS game loop
- Event-driven architecture
- State machine for game screens
- Modular component system

### UI System
- Pygame-based rendering
- Custom button implementations
- Particle effects system
- Responsive design patterns

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Python and Pygame
- Uses N-gram language modeling techniques
- Inspired by modern typing test applications
- Designed for educational and practice purposes

---

**Happy Typing! 🎯⌨️**
