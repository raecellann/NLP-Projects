"""
Game Controller for the N-Grams Typing Test application.
Orchestrates all game components and manages the main game loop.
"""

import pygame
import sys
from constants import *
from game_states import MenuState, PlayGameState, ResultsState
from game_logic import GameLogic
from particles import ParticleSystem


class GameController:
    """Main game controller that manages all game components."""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Initialize display
        self.current_width = MENU_WIDTH
        self.current_height = MENU_HEIGHT
        self.screen = pygame.display.set_mode((self.current_width, self.current_height))
        pygame.display.set_caption("N-Gram Typing Challenge - Modern Edition")
        
        # Initialize game components
        self.clock = pygame.time.Clock()
        self.game_logic = GameLogic()
        self.particle_system = ParticleSystem(self.current_width, self.current_height)
        
        # Initialize fonts
        self.font_title = pygame.font.Font(None, 84)
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 28)
        
        # Load background image
        try:
            self.menu_background = pygame.image.load("multimedia/bg.png")
            self.menu_background = pygame.transform.scale(self.menu_background, (MENU_WIDTH, MENU_HEIGHT))
        except Exception as e:
            print(f"Error loading menu background: {e}")
            self.menu_background = None
        
        # Initialize game states
        self.state = MENU
        self.states = {
            MENU: MenuState(self),
            GAME: PlayGameState(self),
            RESULTS: ResultsState(self)
        }
        
        # Game settings
        self.time_limit = 60
        self.difficulty = "Medium"
        
        # Particle effects
        self.particles = []
    
    def resize_window(self, width: int, height: int):
        """Resize the game window."""
        self.current_width = width
        self.current_height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.particle_system.resize(width, height)
    
    def start_game(self, difficulty: str):
        """Start a new game with the specified difficulty."""
        self.difficulty = difficulty
        self.game_logic.start_game(difficulty)
        self.state = GAME
    
    def end_game(self):
        """End the current game and show results."""
        self.game_logic.end_game()
        self.state = RESULTS
    
    def quit_game(self):
        """Quit the game."""
        pygame.quit()
        sys.exit()
    
    def create_particles(self, x: int, y: int, color: tuple, count: int = 12):
        """Create particle effects at the specified location."""
        for _ in range(count):
            import random
            vx = random.uniform(-3, 3)
            vy = random.uniform(-5, -2)
            particle = self.particle_system.create_particle(x, y, color, (vx, vy))
            self.particles.append(particle)
    
    def update_particles(self):
        """Update all particle effects."""
        self.particle_system.update_particles()
        self.particles = [p for p in self.particles if p.life > 0]
    
    def handle_events(self):
        """Handle all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle typing input
            elif event.type == pygame.KEYDOWN:
                if self.state == GAME:
                    success, message = self.game_logic.handle_typing(event)
                    if not success and message == "game_complete":
                        self.end_game()
                    elif message == "correct":
                        self.create_particles(GAME_WIDTH // 2, GAME_HEIGHT // 2, SUCCESS_GREEN, 8)
                    elif message == "incorrect":
                        self.create_particles(GAME_WIDTH // 2, GAME_HEIGHT // 2, ERROR_RED, 5)
            
            # Handle mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                current_state = self.states.get(self.state)
                if current_state:
                    current_state.handle_event(event)
        
        return True
    
    def update(self):
        """Update game state."""
        mouse_pos = pygame.mouse.get_pos()
        current_state = self.states.get(self.state)
        if current_state:
            current_state.update(mouse_pos)
        
        self.update_particles()
    
    def draw(self):
        """Draw the current game state."""
        current_state = self.states.get(self.state)
        if current_state:
            current_state.draw()
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
    
    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    # Property accessors for game states
    @property
    def typing_text(self):
        return self.game_logic.typing_text
    
    @property
    def target_text(self):
        return self.game_logic.target_text
    
    @property
    def start_time(self):
        return self.game_logic.start_time
    
    @property
    def is_typing(self):
        return self.game_logic.is_typing
    
    @property
    def current_char_index(self):
        return self.game_logic.current_char_index
    
    @property
    def correct_chars(self):
        return self.game_logic.correct_chars
    
    @property
    def total_chars(self):
        return self.game_logic.total_chars
    
    @property
    def wpm(self):
        return self.game_logic.wpm
    
    @property
    def accuracy(self):
        return self.game_logic.accuracy
    
    @property
    def elapsed_time(self):
        return self.game_logic.elapsed_time
    
    @property
    def time_remaining(self):
        return self.game_logic.get_time_remaining()
    
    @property
    def render_start_index(self):
        return self.game_logic.render_start_index


def run_typing_test_with_ngrams(difficulty: str = "medium", time_limit: int = 60):
    """Convenience function to run the typing test."""
    try:
        controller = GameController()
        controller.time_limit = time_limit
        controller.difficulty = difficulty.capitalize()
        controller.run()
    except Exception as e:
        print(f"Error starting typing test: {e}")
        print("Make sure pygame is installed: pip install pygame")


if __name__ == "__main__":
    controller = GameController()
    controller.run()
