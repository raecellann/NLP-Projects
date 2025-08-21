"""
Game States for the N-Grams Typing Test application.
Contains classes for different game screens and their rendering logic.
"""

import pygame
import time
import math
from typing import Dict, Any
from constants import *
from ui_components import ButtonFactory
from particles import ParticleSystem


class GameState:
    """Base class for all game states."""
    
    def __init__(self, game_controller):
        self.game_controller = game_controller
        self.screen = game_controller.screen
        self.font_title = game_controller.font_title
        self.font_large = game_controller.font_large
        self.font_medium = game_controller.font_large
        self.font_small = game_controller.font_small
        self.font_tiny = game_controller.font_tiny
    
    def update(self, mouse_pos):
        """Update state logic."""
        pass
    
    def draw(self):
        """Draw the state."""
        pass
    
    def handle_event(self, event):
        """Handle pygame events."""
        pass


class MenuState(GameState):
    """Menu screen state."""
    
    def __init__(self, game_controller):
        super().__init__(game_controller)
        self.buttons = ButtonFactory.create_menu_buttons()
        self.menu_background = game_controller.menu_background
        self.particle_system = ParticleSystem(MENU_WIDTH, MENU_HEIGHT)
        self.menu_animation_time = 0
        self.title_glow = 0
        self.background_shift = 0
    
    def update(self, mouse_pos):
        """Update menu state."""
        for button in self.buttons.values():
            button.update(mouse_pos)
        self.particle_system.update_particles()
        self.menu_animation_time += 0.008
        self.background_shift += 0.002
    
    def draw(self):
        """Draw the menu screen."""
        # Ensure we're using menu size
        if (self.game_controller.current_width != MENU_WIDTH or 
            self.game_controller.current_height != MENU_HEIGHT):
            self.game_controller.resize_window(MENU_WIDTH, MENU_HEIGHT)
        
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
        else:
            self._draw_modern_background()
            self.particle_system.draw_particles(self.screen)
        
        # Title and subtitle removed - only buttons will be displayed
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)
    
    def _draw_modern_background(self):
        """Draw the animated background."""
        self.screen.fill(BG_DARKEST)
        for y in range(0, MENU_HEIGHT, 2):
            ratio = y / MENU_HEIGHT
            time_offset = math.sin(self.menu_animation_time + ratio * 2) * 0.02
            r = int(GRADIENT_START[0] * (1 - ratio + time_offset) + GRADIENT_END[0] * (ratio - time_offset))
            g = int(GRADIENT_START[1] * (1 - ratio + time_offset) + GRADIENT_END[1] * (ratio - time_offset))
            b = int(GRADIENT_START[2] * (1 - ratio + time_offset) + GRADIENT_END[2] * (ratio - time_offset))
            r = max(8, min(25, r))
            g = max(12, min(35, g))
            b = max(18, min(45, b))
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (MENU_WIDTH, y))
        
        for i in range(3):
            offset = (self.background_shift + i * 0.3) % MENU_WIDTH
            alpha = 30 - i * 8
            accent_surf = pygame.Surface((200, 2), pygame.SRCALPHA)
            pygame.draw.rect(accent_surf, (*PRIMARY_BLUE, alpha), accent_surf.get_rect())
            self.screen.blit(accent_surf, (offset, 100 + i * 200))
    
    def handle_event(self, event):
        """Handle menu events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons["easy"].is_clicked(event):
                self.game_controller.start_game("Easy")
            elif self.buttons["medium"].is_clicked(event):
                self.game_controller.start_game("Medium")
            elif self.buttons["hard"].is_clicked(event):
                self.game_controller.start_game("Hard")
            elif self.buttons["custom"].is_clicked(event):
                self._cycle_time_limit()
            elif self.buttons["exit"].is_clicked(event):
                self.game_controller.quit_game()
    
    def _cycle_time_limit(self):
        """Cycle through available time limits."""
        current_time = self.game_controller.time_limit
        current_index = TIME_LIMITS.index(current_time) if current_time in TIME_LIMITS else 2
        next_index = (current_index + 1) % len(TIME_LIMITS)
        self.game_controller.time_limit = TIME_LIMITS[next_index]
        self.buttons["custom"].text = f"Time: {TIME_LIMITS[next_index]}s"


class PlayGameState(GameState):
    """Main game play state."""
    
    def __init__(self, game_controller):
        super().__init__(game_controller)
        self.buttons = ButtonFactory.create_game_buttons()
        self.particle_system = ParticleSystem(GAME_WIDTH, GAME_HEIGHT)
        self.render_start_index = 0
    
    def update(self, mouse_pos):
        """Update game state."""
        for button in self.buttons.values():
            button.update(mouse_pos)
        self.particle_system.update_particles()
        
        # Update time remaining
        if self.game_controller.is_typing:
            elapsed = time.time() - self.game_controller.start_time
            self.game_controller.time_remaining = max(0, self.game_controller.time_limit - elapsed)
            if self.game_controller.time_remaining <= 0:
                self.game_controller.end_game()
    
    def draw(self):
        """Draw the game screen."""
        # Ensure we're using game size
        if (self.game_controller.current_width != GAME_WIDTH or 
            self.game_controller.current_height != GAME_HEIGHT):
            self.game_controller.resize_window(GAME_WIDTH, GAME_HEIGHT)
        
        self._draw_modern_background()
        self.particle_system.draw_particles(self.screen)
        
        # Draw header
        self._draw_header()
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)
        
        # Draw info panels
        self._draw_info_panels()
        
        # Draw typing area
        self._draw_typing_area()
        
        # Draw progress bar
        if self.game_controller.total_chars > 0:
            self._draw_progress_bar()
    
    def _draw_modern_background(self):
        """Draw the animated background."""
        self.screen.fill(BG_DARKEST)
        for y in range(0, GAME_HEIGHT, 2):
            ratio = y / GAME_HEIGHT
            r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
            g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
            b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)
            r = max(8, min(25, r))
            g = max(12, min(35, g))
            b = max(18, min(45, b))
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (GAME_WIDTH, y))
    
    def _draw_header(self):
        """Draw the game header."""
        header_rect = pygame.Rect(0, 0, GAME_WIDTH, 140)
        header_surf = pygame.Surface((GAME_WIDTH, 140), pygame.SRCALPHA)
        pygame.draw.rect(header_surf, (*BG_DARK, 200), header_surf.get_rect())
        pygame.draw.rect(header_surf, (*WHITE, 20), header_surf.get_rect(), 1)
        self.screen.blit(header_surf, header_rect)
    
    def _draw_info_panels(self):
        """Draw information panels."""
        panel_width = 180
        panel_height = 35
        panel_spacing = 10
        start_x = GAME_WIDTH - (panel_width * 3 + panel_spacing * 2 + 20)
        panel_y = 60
        
        info_panels = [
            (f" {self.game_controller.difficulty}", PRIMARY_BLUE, start_x, panel_y),
            (f" {self.game_controller.time_remaining:.1f}s" if self.game_controller.is_typing else " Start typing", 
             SECONDARY_BLUE, start_x + panel_width + panel_spacing, panel_y),
        ]
        
        if self.game_controller.is_typing:
            typed_chars = len(self.game_controller.typing_text)
            if typed_chars > 0:
                accuracy = (self.game_controller.correct_chars / typed_chars) * 100
                info_panels.append((f" {accuracy:.1f}%", SUCCESS_GREEN, 
                                  start_x + (panel_width + panel_spacing) * 2, panel_y))
        
        for text, color, x, y in info_panels:
            panel_rect = pygame.Rect(x, y, panel_width, panel_height)
            panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, (*BG_DARK, 220), panel_surf.get_rect(), border_radius=12)
            pygame.draw.rect(panel_surf, (*color, 100), panel_surf.get_rect(), 2, border_radius=12)
            self.screen.blit(panel_surf, panel_rect)
            text_surface = self.font_tiny.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=panel_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_typing_area(self):
        """Draw the main typing area."""
        typing_area = pygame.Rect(10, 160, GAME_WIDTH - 20, 360)
        typing_surf = pygame.Surface((typing_area.width, typing_area.height), pygame.SRCALPHA)
        pygame.draw.rect(typing_surf, (*BG_MEDIUM, 180), typing_surf.get_rect(), border_radius=25)
        pygame.draw.rect(typing_surf, (*WHITE, 30), typing_surf.get_rect(), 2, border_radius=25)
        inner_rect = pygame.Rect(15, 15, typing_area.width - 30, typing_area.height - 30)
        pygame.draw.rect(typing_surf, (*BG_DARK, 100), inner_rect, border_radius=20)
        self.screen.blit(typing_surf, typing_area)
        
        if self.game_controller.target_text:
            self._draw_target_text(typing_area)
    
    def _draw_target_text(self, area):
        """Draw the target text with proper formatting."""
        margin_x = 40
        margin_y = 40
        x0 = area.x + margin_x
        y0 = area.y + margin_y
        max_x = area.x + area.width - margin_x
        max_y = area.y + area.height - margin_y
        line_step = 70
        caret_index = min(len(self.game_controller.typing_text), len(self.game_controller.target_text))
        
        if self.render_start_index > caret_index:
            self.render_start_index = max(0, caret_index - 50)
        
        # Simulate text layout to find proper starting position
        def simulate(start_idx: int):
            x = x0
            y = y0
            line_starts = [start_idx]
            caret_pos = None
            for abs_idx in range(start_idx, len(self.game_controller.target_text)):
                ch = self.game_controller.target_text[abs_idx]
                char_surface = self.font_medium.render(ch, True, WHITE)
                w = char_surface.get_width()
                if x + w > max_x:
                    x = x0
                    y += line_step
                    line_starts.append(abs_idx)
                    if y + self.font_medium.get_height() > max_y:
                        break
                if abs_idx == caret_index:
                    caret_pos = (x, y)
                x += w
                if y + self.font_medium.get_height() > max_y:
                    break
            return line_starts, caret_pos
        
        line_starts, caret_pos = simulate(self.render_start_index)
        if caret_pos is None or (caret_pos[1] + self.font_medium.get_height() > max_y):
            probe_start = max(0, caret_index - 200)
            self.render_start_index = probe_start
            for _ in range(12):
                ls, cp = simulate(self.render_start_index)
                if cp is None:
                    break
                if cp[1] + self.font_medium.get_height() <= max_y:
                    break
                if len(ls) >= 2:
                    self.render_start_index = ls[1]
                else:
                    self.render_start_index += 5
            line_starts, caret_pos = simulate(self.render_start_index)
        
        # Draw the text
        x = x0
        y = y0
        cursor_drawn = False
        
        for abs_idx in range(self.render_start_index, len(self.game_controller.target_text)):
            ch = self.game_controller.target_text[abs_idx]
            if abs_idx < len(self.game_controller.typing_text):
                color = SUCCESS_GREEN if self.game_controller.typing_text[abs_idx] == ch else ERROR_RED
            else:
                color = (100, 100, 100)
            
            char_surface = self.font_medium.render(ch, True, color)
            shadow_surface = self.font_medium.render(ch, True, (*BLACK, 80))
            w = char_surface.get_width()
            
            if x + w > max_x:
                x = x0
                y += line_step
                if y + self.font_medium.get_height() > max_y:
                    break
            
            self.screen.blit(shadow_surface, (x + 1, y + 1))
            self.screen.blit(char_surface, (x, y))
            
            # Draw cursor
            if not cursor_drawn and abs_idx == caret_index and self.game_controller.is_typing:
                cursor_time = time.time() * 2
                if int(cursor_time) % 2 == 0:
                    cursor_height = self.font_medium.get_height()
                    pygame.draw.line(self.screen, PRIMARY_BLUE, (x, y), (x, y + cursor_height), 3)
                cursor_drawn = True
            
            x += w
            if y + self.font_medium.get_height() > max_y:
                break
        
        # Draw cursor at start if not drawn elsewhere
        if not cursor_drawn and self.game_controller.is_typing:
            cursor_time = time.time() * 2
            if int(cursor_time) % 2 == 0:
                cursor_height = self.font_medium.get_height()
                pygame.draw.line(self.screen, PRIMARY_BLUE, (x0, y0), (x0, y0 + cursor_height), 3)
    
    def _draw_progress_bar(self):
        """Draw the progress bar."""
        progress = self.game_controller.correct_chars / self.game_controller.total_chars
        progress_width = (GAME_WIDTH - 120) * progress
        progress_bg_rect = pygame.Rect(60, 700, GAME_WIDTH - 120, 30)
        progress_bg_surf = pygame.Surface((progress_bg_rect.width, progress_bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(progress_bg_surf, (*BG_DARK, 200), progress_bg_surf.get_rect(), border_radius=15)
        pygame.draw.rect(progress_bg_surf, (*WHITE, 30), progress_bg_surf.get_rect(), 2, border_radius=15)
        self.screen.blit(progress_bg_surf, progress_bg_rect)
        
        if progress > 0:
            progress_rect = pygame.Rect(60, 700, progress_width, 30)
            progress_surf = pygame.Surface((progress_width, 30), pygame.SRCALPHA)
            for x in range(int(progress_width)):
                ratio = x / progress_width
                r = int(SUCCESS_GREEN[0] * (1 - ratio) + PRIMARY_BLUE[0] * ratio)
                g = int(SUCCESS_GREEN[1] * (1 - ratio) + PRIMARY_BLUE[1] * ratio)
                b = int(SUCCESS_GREEN[2] * (1 - ratio) + PRIMARY_BLUE[2] * ratio)
                pygame.draw.line(progress_surf, (r, g, b), (x, 0), (x, 30))
            self.screen.blit(progress_surf, progress_rect)
        
        progress_text = f"Progress: {self.game_controller.correct_chars}/{self.game_controller.total_chars} ({progress*100:.1f}%)"
        progress_surface = self.font_tiny.render(progress_text, True, WHITE)
        self.screen.blit(progress_surface, (60, 740))
    
    def handle_event(self, event):
        """Handle game events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons["restart"].is_clicked(event):
                self.game_controller.start_game(self.game_controller.difficulty)
            elif self.buttons["menu"].is_clicked(event):
                self.game_controller.state = MENU


class ResultsState(GameState):
    """Results screen state."""
    
    def __init__(self, game_controller):
        super().__init__(game_controller)
        self.buttons = ButtonFactory.create_results_buttons()
        self.particle_system = ParticleSystem(GAME_WIDTH, GAME_HEIGHT)
    
    def update(self, mouse_pos):
        """Update results state."""
        for button in self.buttons.values():
            button.update(mouse_pos)
        self.particle_system.update_particles()
    
    def draw(self):
        """Draw the results screen."""
        # Ensure we're using game size
        if (self.game_controller.current_width != GAME_WIDTH or 
            self.game_controller.current_height != GAME_HEIGHT):
            self.game_controller.resize_window(GAME_WIDTH, GAME_HEIGHT)

        self._draw_modern_background()
        self.particle_system.draw_particles(self.screen)

        # Draw results panel
        panel_rect = pygame.Rect(80, 60, GAME_WIDTH - 160, GAME_HEIGHT - 120)
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (*BG_MEDIUM, 220), panel_surf.get_rect(), border_radius=40)
        pygame.draw.rect(panel_surf, (*WHITE, 80), panel_surf.get_rect(), 6, border_radius=40)
        inner_rect = pygame.Rect(25, 25, panel_rect.width - 50, panel_rect.height - 50)
        pygame.draw.rect(panel_surf, (*BG_DARK, 80), inner_rect, border_radius=30)
        self.screen.blit(panel_surf, panel_rect)

        # Draw title
        title_text = "🎉 Typing Test Complete!"
        title_surface = self.font_large.render(title_text, True, PRIMARY_BLUE)
        title_rect = title_surface.get_rect(center=(GAME_WIDTH // 2, 140))
        self.screen.blit(title_surface, title_rect)

        # Draw results
        y_offset = 220
        results = [
            (f" Time: {self.game_controller.elapsed_time:.2f} sec", PRIMARY_BLUE),
            (f" Characters: {self.game_controller.correct_chars}/{self.game_controller.total_chars}", SUCCESS_GREEN),
            (f" Accuracy: {self.game_controller.accuracy:.1f}%", WARNING_ORANGE),
            (f" Speed: {self.game_controller.wpm:.1f} WPM", ACCENT_BLUE)
        ]
        
        for result_text, color in results:
            result_surface = self.font_medium.render(result_text, True, color)
            result_rect = result_surface.get_rect(center=(GAME_WIDTH // 2, y_offset))
            self.screen.blit(result_surface, result_rect)
            y_offset += 60

        # Draw feedback
        feedback = self._get_performance_feedback()
        feedback_surface = self.font_medium.render(feedback, True, SUCCESS_GREEN)
        feedback_rect = feedback_surface.get_rect(center=(GAME_WIDTH // 2, y_offset))
        self.screen.blit(feedback_surface, feedback_rect)

        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)
    
    def _draw_modern_background(self):
        """Draw the animated background."""
        self.screen.fill(BG_DARKEST)
        for y in range(0, GAME_HEIGHT, 2):
            ratio = y / GAME_HEIGHT
            r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
            g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
            b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)
            r = max(8, min(25, r))
            g = max(12, min(35, g))
            b = max(18, min(45, b))
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (GAME_WIDTH, y))
    
    def _get_performance_feedback(self):
        """Get performance feedback based on results."""
        if self.game_controller.accuracy >= 95 and self.game_controller.wpm >= 60:
            return "🏆 Outstanding! You're a typing master!"
        elif self.game_controller.accuracy >= 85 and self.game_controller.wpm >= 40:
            return "👏 Excellent performance! Keep it up!"
        elif self.game_controller.accuracy >= 70 and self.game_controller.wpm >= 25:
            return "✅ Good job! Room for improvement."
        else:
            return "📚 Keep practicing! You'll get better!"
    
    def handle_event(self, event):
        """Handle results events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons["play_again"].is_clicked(event):
                self.game_controller.start_game(self.game_controller.difficulty)
            elif self.buttons["back_to_menu"].is_clicked(event):
                self.game_controller.state = MENU 
