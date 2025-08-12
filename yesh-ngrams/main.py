import os
import pygame
from gui import TypingInterface
from typing_logic import TypingTestLogic


class TypingTestApp:
    def __init__(self, width: int = 1200, height: int = 720):
        pygame.init()
        pygame.display.set_caption('WPM Typing Test - N-Grams (pygame)')
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        # Initialize components
        self.gui = TypingInterface(width, height)
        self.logic = TypingTestLogic()

        # Set initial time button state
        self.gui.set_time_button_active(self.logic.get_test_duration())

    def handle_events(self):
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resizing
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.gui.resize(event.w, event.h)

        # Handle GUI events
        gui_result = self.gui.handle_events(events)
        
        # Process GUI results
        if gui_result['time_button_clicked']:
            duration = gui_result['time_button_clicked']
            self.logic.set_test_duration(duration)
            self.gui.set_time_button_active(duration)
            # Update time immediately if a test is active by restarting
            if self.logic.is_test_active():
                self.logic.new_test()

        if gui_result['new_test_clicked']:
            self.logic.new_test()
            self.gui.clear_input()
            self.gui.activate_input_field()

        if gui_result['reset_clicked']:
            self.logic.reset_test()
            self.gui.clear_input()
            self.gui.deactivate_input_field()

        # Handle input text
        if gui_result['input_text']:
            if not self.logic.is_test_active():
                # Start test on first typing interaction
                self.logic.start_test()
                # Activate the input field
                self.gui.activate_input_field()
            
            # Process the word input
            self.logic.process_word_input(gui_result['input_text'])
            self.gui.clear_input()

        # Handle input field activation (clicking on it)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.gui.input_field.rect.collidepoint(event.pos):
                    if not self.logic.is_test_active():
                        # Start test when clicking input field
                        self.logic.start_test()
                    self.gui.activate_input_field()

        # Handle keyboard shortcuts
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Ctrl+Shift+Enter -> new test
                if (event.key == pygame.K_RETURN and 
                    (event.mod & pygame.KMOD_CTRL) and 
                    (event.mod & pygame.KMOD_SHIFT)):
                    self.logic.new_test()
                    self.gui.clear_input()

        return True

    def update(self, dt: float):
        # Update GUI components
        self.gui.update(dt)
        
        # Check if test should end
        if self.logic.check_test_end():
            pass  # Test ended, results will be shown

    def draw(self):
        # Clear screen
        self.screen.fill(self.gui.colors['bg'])

        # Get current state
        is_active = self.logic.is_test_active()
        elapsed = self.logic.elapsed_seconds()
        remaining = self.logic.remaining_seconds()
        wpm = self.logic.calculate_current_wpm(elapsed)
        accuracy = self.logic.calculate_current_accuracy()
        
        words = self.logic.get_words()
        current_word_index = self.logic.get_current_word_index()
        typed_words = self.logic.get_typed_words()
        
        test_started = self.logic.has_test_started_once()
        results = self.logic.get_results()

        # Draw GUI components
        self.gui.draw_header(self.screen)
        self.gui.draw_config(self.screen)
        self.gui.draw_live_stats(self.screen, is_active, elapsed, remaining, wpm, accuracy)
        self.gui.draw_text_area(self.screen, words, current_word_index, typed_words, is_active)
        self.gui.draw_input(self.screen, is_active)
        self.gui.draw_results_panel(self.screen, is_active, test_started, results)

        # Update display
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # Convert to seconds
            
            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()


def main():
    # Ensure we run from project directory so relative corpora path works
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    app = TypingTestApp()
    app.run()


if __name__ == '__main__':
    main()
