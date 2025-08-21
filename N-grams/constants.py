"""
Constants and configuration for the N-Grams Typing Test application.
"""

# Window dimensions
MENU_WIDTH = 1200
MENU_HEIGHT = 650
GAME_WIDTH = 1280
GAME_HEIGHT = 650

# Game settings
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURE_WHITE = (255, 255, 255)
OFF_WHITE = (245, 245, 245)
LIGHT_GRAY = (220, 220, 220)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Primary colors
PRIMARY_BLUE = (64, 156, 255)
SECONDARY_BLUE = (52, 152, 219)
ACCENT_BLUE = (155, 89, 182)
DEEP_BLUE = (41, 128, 185)

# Success colors
SUCCESS_GREEN = (46, 213, 115)
SUCCESS_DARK = (39, 174, 96)

# Warning colors
WARNING_ORANGE = (255, 159, 67)
WARNING_DARK = (230, 126, 34)

# Error colors
ERROR_RED = (255, 107, 107)
ERROR_DARK = (231, 76, 60)

# Neutral colors
NEUTRAL_GRAY = (149, 165, 166)
NEUTRAL_DARK = (127, 140, 141)

# Background colors
BG_DARKEST = (8, 12, 18)
BG_DARKER = (12, 18, 28)
BG_DARK = (18, 25, 38)
BG_MEDIUM = (25, 35, 50)
BG_LIGHT = (35, 45, 65)

# Glass effect colors
GLASS_DARK = (20, 30, 45, 180)
GLASS_MEDIUM = (30, 40, 55, 160)
GLASS_LIGHT = (40, 50, 70, 140)

# Gradient colors
GRADIENT_START = (12, 18, 28)
GRADIENT_END = (18, 25, 38)
GRADIENT_ACCENT = (25, 35, 50)

# Game states
MENU = "menu"
GAME = "game"
RESULTS = "results"
SETTINGS = "settings"

# Difficulty settings
DIFFICULTY_SETTINGS = {
    "Easy": {
        "n_gram": 2,
        "base_target_len": 6,
        "avg_word_len": 3.5
    },
    "Medium": {
        "n_gram": 3,
        "base_target_len": 8,
        "avg_word_len": 6.0
    },
    "Hard": {
        "n_gram": 4,
        "base_target_len": 10,
        "avg_word_len": 8.0
    }
}

# Time limits
TIME_LIMITS = [15, 30, 60, 120]

# UI dimensions
BUTTON_DIMENSIONS = {
    "row_button": (260, 54),
    "results_button": (220, 50),
    "game_button": (140, 50)
}

# Spacing
UI_SPACING = {
    "gap": 40,
    "second_gap": 80,
    "results_spacing": 40
} 