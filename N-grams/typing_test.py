import pygame
import sys
import time
import random
import math
from typing import List, Tuple, Optional
from ngrams import Ngrams

pygame.init()
pygame.mixer.init()

MENU_WIDTH = 1200
MENU_HEIGHT = 650

GAME_WIDTH = 1280
GAME_HEIGHT = 650

FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURE_WHITE = (255, 255, 255)
OFF_WHITE = (245, 245, 245)
LIGHT_GRAY = (220, 220, 220)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

PRIMARY_BLUE = (64, 156, 255)
SECONDARY_BLUE = (52, 152, 219)
ACCENT_BLUE = (155, 89, 182)
DEEP_BLUE = (41, 128, 185)

SUCCESS_GREEN = (46, 213, 115)
SUCCESS_DARK = (39, 174, 96)

WARNING_ORANGE = (255, 159, 67)
WARNING_DARK = (230, 126, 34)

ERROR_RED = (255, 107, 107)
ERROR_DARK = (231, 76, 60)

NEUTRAL_GRAY = (149, 165, 166)
NEUTRAL_DARK = (127, 140, 141)

BG_DARKEST = (8, 12, 18)
BG_DARKER = (12, 18, 28)
BG_DARK = (18, 25, 38)
BG_MEDIUM = (25, 35, 50)
BG_LIGHT = (35, 45, 65)

GLASS_DARK = (20, 30, 45, 180)
GLASS_MEDIUM = (30, 40, 55, 160)
GLASS_LIGHT = (40, 50, 70, 140)

GRADIENT_START = (12, 18, 28)
GRADIENT_END = (18, 25, 38)
GRADIENT_ACCENT = (25, 35, 50)

MENU = "menu"
GAME = "game"
RESULTS = "results"
SETTINGS = "settings"

class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], velocity: Tuple[float, float]):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.035)
        self.size = random.randint(2, 6)
        self.original_size = self.size
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)
        self.alpha = 255
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12
        self.life -= self.decay
        self.size = max(0, self.original_size * self.life)
        self.rotation += self.rotation_speed
        self.alpha = int(255 * self.life)
        self.vx += random.uniform(-0.05, 0.05)
    
    def draw(self, screen):
        if self.life > 0:
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            points = []
            for i in range(4):
                angle = (i * 90 + self.rotation) * math.pi / 180
                radius = self.size
                x = self.size + radius * math.cos(angle)
                y = self.size + radius * math.sin(angle)
                points.append((x, y))
            if len(points) >= 3:
                pygame.draw.polygon(surf, self.color, points)
                surf.set_alpha(self.alpha)
            screen.blit(surf, (self.x - self.size, self.y - self.size))

class ModernButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int] = PRIMARY_BLUE, hover_color: Tuple[int, int, int] = SECONDARY_BLUE,
                 icon: str = "", font_size: int = 32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.icon = icon
        self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.animation_time = 0
        self.scale = 1.0
        self.target_scale = 1.0
        self.glow_intensity = 0
        self.pressed = False
        
    def update(self, mouse_pos: Tuple[int, int]):
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and not was_hovered:
            self.target_scale = 1.02
            self.glow_intensity = 1.0
        elif not self.hovered and was_hovered:
            self.target_scale = 1.0
            self.glow_intensity = 0.0
        self.scale += (self.target_scale - self.scale) * 0.15
        if self.hovered:
            self.glow_intensity += (1.0 - self.glow_intensity) * 0.1
        else:
            self.glow_intensity += (0.0 - self.glow_intensity) * 0.1
        self.current_color = self.hover_color if self.hovered else self.color
        if self.hovered:
            self.animation_time += 0.1
        else:
            self.animation_time = 0
    
    def draw(self, screen):
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_x = self.rect.centerx - scaled_width // 2
        scaled_y = self.rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        if self.glow_intensity > 0:
            glow_rect = scaled_rect.inflate(20, 20)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_alpha = int(50 * self.glow_intensity)
            pygame.draw.rect(glow_surf, (*self.current_color, glow_alpha), glow_surf.get_rect(), border_radius=18)
            screen.blit(glow_surf, glow_rect)
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += 6
        shadow_rect.y += 6
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (*BLACK, 40), shadow_surf.get_rect(), border_radius=18)
        screen.blit(shadow_surf, shadow_rect)
        gradient_surf = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        for y in range(scaled_rect.height):
            ratio = y / scaled_rect.height
            r = int(self.current_color[0] * (1 - ratio * 0.3) + self.hover_color[0] * (ratio * 0.3))
            g = int(self.current_color[1] * (1 - ratio * 0.3) + self.hover_color[1] * (ratio * 0.3))
            b = int(self.current_color[2] * (1 - ratio * 0.3) + self.hover_color[2] * (ratio * 0.3))
            pygame.draw.line(gradient_surf, (r, g, b), (0, y), (scaled_rect.width, y))
        screen.blit(gradient_surf, scaled_rect)
        border_color = tuple(min(255, c + int(20 * self.glow_intensity)) for c in self.current_color)
        pygame.draw.rect(screen, border_color, scaled_rect, 2, border_radius=18)
        highlight_rect = scaled_rect.copy()
        highlight_rect.height = highlight_rect.height // 2
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (*WHITE, 25), highlight_surf.get_rect(), border_radius=18)
        screen.blit(highlight_surf, highlight_rect)
        display_text = f"{self.icon} {self.text}" if self.icon else self.text
        text_surface = self.font.render(display_text, True, WHITE)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        shadow_surface = self.font.render(display_text, True, (*BLACK, 100))
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class OutlineButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 border_color: Tuple[int, int, int], font_size: int = 32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.border_color = border_color
        try:
            self.font = pygame.font.SysFont("Consolas", font_size)
        except Exception:
            self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.scale = 1.0
        self.target_scale = 1.0
        self.hover_glow = 0.0
        self.click_flash = 0.0

    def _lighten(self, color: Tuple[int, int, int], amount: float) -> Tuple[int, int, int]:
        r, g, b = color
        return (
            min(255, int(r + (255 - r) * amount)),
            min(255, int(g + (255 - g) * amount)),
            min(255, int(b + (255 - b) * amount)),
        )

    def update(self, mouse_pos: Tuple[int, int]):
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and not was_hovered:
            self.target_scale = 1.02
        elif not self.hovered and was_hovered:
            self.target_scale = 1.0
        self.scale += (self.target_scale - self.scale) * 0.15
        target_hover = 0.25 if self.hovered else 0.0
        self.hover_glow += (target_hover - self.hover_glow) * 0.12
        self.click_flash = max(0.0, self.click_flash - 0.06)

    def draw(self, screen):
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_x = self.rect.centerx - scaled_width // 2
        scaled_y = self.rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        total_glow = min(0.8, self.hover_glow + self.click_flash)
        if total_glow > 0:
            base_color = self._lighten(self.border_color, 0.6)
            layers = 6
            for i in range(layers):
                inflate = 16 + i * 10
                alpha = int(60 * total_glow * (1 - i / layers))
                if alpha <= 0:
                    continue
                glow_rect = scaled_rect.inflate(inflate, inflate)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                br = max(8, 10 + i * 2)
                pygame.draw.rect(glow_surf, (*base_color, alpha), glow_surf.get_rect(), border_radius=br)
                screen.blit(glow_surf, glow_rect)
        fill_color = self._lighten(self.border_color, 0.25)
        pygame.draw.rect(screen, fill_color, scaled_rect, border_radius=12)
        light_border = self._lighten(self.border_color, 0.25)
        pygame.draw.rect(screen, light_border, scaled_rect, 3, border_radius=12)
        inner_rect = scaled_rect.inflate(-6, -6)
        inner_color = self._lighten(self.border_color, 0.45)
        pygame.draw.rect(screen, inner_color, inner_rect, 1, border_radius=10)
        text_surface = self.font.render(self.text, True, PURE_WHITE)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        shadow_surface = self.font.render(self.text, True, (*BLACK, 120))
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.click_flash = 0.6
            return True
        return False

class TypingGame:
    def __init__(self):
        self.current_width = MENU_WIDTH
        self.current_height = MENU_HEIGHT
        self.screen = pygame.display.set_mode((self.current_width, self.current_height))
        pygame.display.set_caption("N-Gram Typing Challenge - Modern Edition")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.Font(None, 84)
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 28)
        try:
            self.menu_background = pygame.image.load("multimedia/bg.png")
            self.menu_background = pygame.transform.scale(self.menu_background, (MENU_WIDTH, MENU_HEIGHT))
        except Exception as e:
            print(f"Error loading menu background: {e}")
            self.menu_background = None
        self.state = MENU
        self.particles = []
        self.background_particles = []
        self.typing_text = ""
        self.target_text = ""
        self.start_time = 0
        self.is_typing = False
        self.current_char_index = 0
        self.correct_chars = 0
        self.total_chars = 0
        self.wpm = 0
        self.accuracy = 0
        self.elapsed_time = 0
        self.difficulty = "Medium"
        self.n_gram = 3
        self.num_phrases = 8
        self.time_limit = 60
        self.time_remaining = self.time_limit
        self.base_target_len = 8
        self.avg_word_len = 6.0
        self.ngrams_obj = None
        self.render_start_index = 0
        self.setup_ui()
        self.generate_background_particles()
        self.menu_animation_time = 0
        self.title_glow = 0
        self.background_shift = 0
        self.sounds = {}
        
    def setup_ui(self):
        row_button_width, row_button_height = 260, 54
        gap = 40
        start_x = MENU_WIDTH // 2 - (3 * row_button_width + 2 * gap) // 2
        row_y = 360
        self.easy_button = OutlineButton(start_x, row_y, row_button_width, row_button_height, "Easy Mode", SUCCESS_GREEN, 26)
        self.medium_button = OutlineButton(start_x + row_button_width + gap, row_y, row_button_width, row_button_height, "Medium Mode", PRIMARY_BLUE, 26)
        self.hard_button = OutlineButton(start_x + (row_button_width + gap) * 2, row_y, row_button_width, row_button_height, "Hard Mode", ERROR_RED, 26)

        second_gap = 80
        start_x2 = MENU_WIDTH // 2 - (2 * row_button_width + second_gap) // 2
        row2_y = row_y + 90
        self.custom_button = OutlineButton(start_x2, row2_y, row_button_width, row_button_height, f"Time: {self.time_limit}s", ACCENT_BLUE, 26)
        self.exit_button = OutlineButton(start_x2 + row_button_width + second_gap, row2_y, row_button_width, row_button_height, "Exit", NEUTRAL_GRAY, 26)

        self.restart_button = ModernButton(60, 60, 140, 50, "Restart", WARNING_ORANGE, WARNING_DARK)
        self.menu_button = ModernButton(210, 60, 140, 50, "Menu", NEUTRAL_GRAY, NEUTRAL_DARK)

        results_button_width, results_button_height = 220, 50
        spacing = 40
        total_width = results_button_width * 2 + spacing
        start_x = GAME_WIDTH // 2 - total_width // 2
        y = GAME_HEIGHT - 150

        self.play_again_button = ModernButton(start_x, y, results_button_width, results_button_height,
                                            "Play Again", SUCCESS_GREEN, SUCCESS_DARK)
        self.back_to_menu_button = ModernButton(start_x + results_button_width + spacing, y,
                                                results_button_width, results_button_height,
                                                "Back to Menu", PRIMARY_BLUE, SECONDARY_BLUE)

    def resize_window(self, width: int, height: int):
        self.current_width = width
        self.current_height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.background_particles.clear()
        self.generate_background_particles()
    
    def generate_background_particles(self):
        for _ in range(60):
            x = random.randint(0, self.current_width)
            y = random.randint(0, self.current_height)
            colors = [PRIMARY_BLUE, SUCCESS_GREEN, ACCENT_BLUE, WARNING_ORANGE]
            color = random.choice(colors)
            vx = random.uniform(-0.2, 0.2)
            vy = random.uniform(-0.2, 0.2)
            particle = Particle(x, y, color, (vx, vy))
            particle.life = random.uniform(0.3, 0.7)
            self.background_particles.append(particle)
    
    def create_particles(self, x: int, y: int, color: Tuple[int, int, int], count: int = 12):
        for _ in range(count):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-5, -2)
            particle = Particle(x, y, color, (vx, vy))
            self.particles.append(particle)
    
    def update_particles(self):
        for particle in self.background_particles:
            particle.update()
            if particle.life <= 0:
                particle.x = random.randint(0, self.current_width)
                particle.y = random.randint(0, self.current_height)
                particle.life = random.uniform(0.3, 0.7)
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
    
    def draw_particles(self):
        for particle in self.background_particles:
            particle.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)
    
    def draw_modern_background(self):
        self.menu_animation_time += 0.008
        self.background_shift += 0.002
        self.screen.fill(BG_DARKEST)
        for y in range(0, self.current_height, 2):
            ratio = y / self.current_height
            time_offset = math.sin(self.menu_animation_time + ratio * 2) * 0.02
            r = int(GRADIENT_START[0] * (1 - ratio + time_offset) + GRADIENT_END[0] * (ratio - time_offset))
            g = int(GRADIENT_START[1] * (1 - ratio + time_offset) + GRADIENT_END[1] * (ratio - time_offset))
            b = int(GRADIENT_START[2] * (1 - ratio + time_offset) + GRADIENT_END[2] * (ratio - time_offset))
            r = max(8, min(25, r))
            g = max(12, min(35, g))
            b = max(18, min(45, b))
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (self.current_width, y))
        for i in range(3):
            offset = (self.background_shift + i * 0.3) % self.current_width
            alpha = 30 - i * 8
            accent_surf = pygame.Surface((200, 2), pygame.SRCALPHA)
            pygame.draw.rect(accent_surf, (*PRIMARY_BLUE, alpha), accent_surf.get_rect())
            self.screen.blit(accent_surf, (offset, 100 + i * 200))
    
    def draw_menu(self):
        if self.current_width != MENU_WIDTH or self.current_height != MENU_HEIGHT:
            self.resize_window(MENU_WIDTH, MENU_HEIGHT)
        
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
        else:
            self.draw_modern_background()
            self.draw_particles()
        mouse_pos = pygame.mouse.get_pos()
        self.easy_button.update(mouse_pos)
        self.medium_button.update(mouse_pos)
        self.hard_button.update(mouse_pos)
        self.custom_button.update(mouse_pos)
        self.exit_button.update(mouse_pos)
        self.easy_button.draw(self.screen)
        self.medium_button.draw(self.screen)
        self.hard_button.draw(self.screen)
        self.custom_button.draw(self.screen)
        self.exit_button.draw(self.screen)
    
    def draw_game(self):
        if self.current_width != GAME_WIDTH or self.current_height != GAME_HEIGHT:
            self.resize_window(GAME_WIDTH, GAME_HEIGHT)
        
        self.draw_modern_background()
        self.draw_particles()
        header_rect = pygame.Rect(0, 0, GAME_WIDTH, 140)
        header_surf = pygame.Surface((GAME_WIDTH, 140), pygame.SRCALPHA)
        pygame.draw.rect(header_surf, (*BG_DARK, 200), header_surf.get_rect())
        pygame.draw.rect(header_surf, (*WHITE, 20), header_surf.get_rect(), 1)
        self.screen.blit(header_surf, header_rect)
        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.update(mouse_pos)
        self.menu_button.update(mouse_pos)
        self.restart_button.draw(self.screen)
        self.menu_button.draw(self.screen)
        if self.is_typing:
            elapsed = time.time() - self.start_time
            self.time_remaining = max(0, self.time_limit - elapsed)
            if self.time_remaining <= 0:
                self.end_game()
        panel_width = 180
        panel_height = 35
        panel_spacing = 10
        start_x = GAME_WIDTH - (panel_width * 3 + panel_spacing * 2 + 20)
        panel_y = 60
        info_panels = [
            (f" {self.difficulty}", PRIMARY_BLUE, start_x, panel_y),
            (f" {self.time_remaining:.1f}s" if self.is_typing else " Start typing", SECONDARY_BLUE, start_x + panel_width + panel_spacing, panel_y),
        ]
        if self.is_typing:
            typed_chars = len(self.typing_text)
            if typed_chars > 0:
                accuracy = (self.correct_chars / typed_chars) * 100
                info_panels.append((f" {accuracy:.1f}%", SUCCESS_GREEN, start_x + (panel_width + panel_spacing) * 2, panel_y))
        for text, color, x, y in info_panels:
            panel_rect = pygame.Rect(x, y, panel_width, panel_height)
            panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, (*BG_DARK, 220), panel_surf.get_rect(), border_radius=12)
            pygame.draw.rect(panel_surf, (*color, 100), panel_surf.get_rect(), 2, border_radius=12)
            self.screen.blit(panel_surf, panel_rect)
            text_surface = self.font_tiny.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=panel_rect.center)
            self.screen.blit(text_surface, text_rect)
        typing_area = pygame.Rect(10, 160, GAME_WIDTH - 20, 360)
        typing_surf = pygame.Surface((typing_area.width, typing_area.height), pygame.SRCALPHA)
        pygame.draw.rect(typing_surf, (*BG_MEDIUM, 180), typing_surf.get_rect(), border_radius=25)
        pygame.draw.rect(typing_surf, (*WHITE, 30), typing_surf.get_rect(), 2, border_radius=25)
        inner_rect = pygame.Rect(15, 15, typing_area.width - 30, typing_area.height - 30)
        pygame.draw.rect(typing_surf, (*BG_DARK, 100), inner_rect, border_radius=20)
        self.screen.blit(typing_surf, typing_area)
        if self.target_text:
            self.draw_target_text(typing_area)
        if self.total_chars > 0:
            progress = self.correct_chars / self.total_chars
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
            progress_text = f"Progress: {self.correct_chars}/{self.total_chars} ({progress*100:.1f}%)"
            progress_surface = self.font_tiny.render(progress_text, True, WHITE)
            self.screen.blit(progress_surface, (60, 740))
    
    def draw_target_text(self, area):
        margin_x = 40
        margin_y = 40
        x0 = area.x + margin_x
        y0 = area.y + margin_y
        max_x = area.x + area.width - margin_x
        max_y = area.y + area.height - margin_y
        line_step = 70
        caret_index = min(len(self.typing_text), len(self.target_text))
        if self.render_start_index > caret_index:
            self.render_start_index = max(0, caret_index - 50)
        def simulate(start_idx: int):
            x = x0
            y = y0
            line_starts = [start_idx]
            caret_pos = None
            for abs_idx in range(start_idx, len(self.target_text)):
                ch = self.target_text[abs_idx]
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
        x = x0
        y = y0
        cursor_drawn = False
        for abs_idx in range(self.render_start_index, len(self.target_text)):
            ch = self.target_text[abs_idx]
            if abs_idx < len(self.typing_text):
                color = SUCCESS_GREEN if self.typing_text[abs_idx] == ch else ERROR_RED
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
            if not cursor_drawn and abs_idx == caret_index and self.is_typing:
                cursor_time = time.time() * 2
                if int(cursor_time) % 2 == 0:
                    cursor_height = self.font_medium.get_height()
                    pygame.draw.line(self.screen, PRIMARY_BLUE, (x, y), (x, y + cursor_height), 3)
                cursor_drawn = True
            x += w
            if y + self.font_medium.get_height() > max_y:
                break
        if not cursor_drawn and self.is_typing:
            cursor_time = time.time() * 2
            if int(cursor_time) % 2 == 0:
                cursor_height = self.font_medium.get_height()
                pygame.draw.line(self.screen, PRIMARY_BLUE, (x0, y0), (x0, y0 + cursor_height), 3)
    
    def draw_results(self):
        if self.current_width != GAME_WIDTH or self.current_height != GAME_HEIGHT:
            self.resize_window(GAME_WIDTH, GAME_HEIGHT)

        self.draw_modern_background()
        self.draw_particles()

        panel_rect = pygame.Rect(80, 60, GAME_WIDTH - 160, GAME_HEIGHT - 120)
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)

        pygame.draw.rect(panel_surf, (*BG_MEDIUM, 220), panel_surf.get_rect(), border_radius=40)
        pygame.draw.rect(panel_surf, (*WHITE, 80), panel_surf.get_rect(), 6, border_radius=40)
        inner_rect = pygame.Rect(25, 25, panel_rect.width - 50, panel_rect.height - 50)
        pygame.draw.rect(panel_surf, (*BG_DARK, 80), inner_rect, border_radius=30)

        self.screen.blit(panel_surf, panel_rect)


        try:
            font_mono_large = pygame.font.SysFont("Consolas", 48)
            font_mono_medium = pygame.font.SysFont("Consolas", 32)
        except:
            font_mono_large = pygame.font.Font(None, 48)
            font_mono_medium = pygame.font.Font(None, 32)

        title_text = " Typing Test Complete!"
        title_surface = font_mono_large.render(title_text, True, PRIMARY_BLUE)
        title_rect = title_surface.get_rect(center=(GAME_WIDTH // 2, 140))
        self.screen.blit(title_surface, title_rect)

        y_offset = 220
        results = [
            (f" Time: {self.elapsed_time:.2f} sec", PRIMARY_BLUE),
            (f" Characters: {self.correct_chars}/{self.total_chars}", SUCCESS_GREEN),
            (f" Accuracy: {self.accuracy:.1f}%", WARNING_ORANGE),
            (f" Speed: {self.wpm:.1f} WPM", ACCENT_BLUE)
        ]
        for result_text, color in results:
            result_surface = font_mono_medium.render(result_text, True, color)
            result_rect = result_surface.get_rect(center=(GAME_WIDTH // 2, y_offset))
            self.screen.blit(result_surface, result_rect)
            y_offset += 60

        feedback = self.get_performance_feedback()
        feedback_surface = font_mono_medium.render(feedback, True, SUCCESS_GREEN)
        feedback_rect = feedback_surface.get_rect(center=(GAME_WIDTH // 2, y_offset))
        self.screen.blit(feedback_surface, feedback_rect)

        mouse_pos = pygame.mouse.get_pos()
        self.play_again_button.update(mouse_pos)
        self.back_to_menu_button.update(mouse_pos)
        self.play_again_button.draw(self.screen)
        self.back_to_menu_button.draw(self.screen)
    
    def get_performance_feedback(self):
        if self.accuracy >= 95 and self.wpm >= 60:
            return " Outstanding! You're a typing master!"
        elif self.accuracy >= 85 and self.wpm >= 40:
            return " Excellent performance! Keep it up!"
        elif self.accuracy >= 70 and self.wpm >= 25:
            return " Good job! Room for improvement."
        else:
            return " Keep practicing! You'll get better!"
    
    def start_game(self, difficulty: str):
        self.difficulty = difficulty
        if difficulty == "Easy":
            self.n_gram = 2
            self.base_target_len = 6
            self.avg_word_len = 3.5
        elif difficulty == "Medium":
            self.n_gram = 3
            self.base_target_len = 8
            self.avg_word_len = 6.0
        elif difficulty == "Hard":
            self.n_gram = 4
            self.base_target_len = 10
            self.avg_word_len = 8.0
        try:
            random.seed()
            
            approx_chars_per_phrase = int(self.base_target_len * (self.avg_word_len + 1))
            min_chars = int(self.time_limit * 8)
            num_phrases = max(5, min(40, (min_chars + approx_chars_per_phrase - 1) // approx_chars_per_phrase))
            
            num_phrases += random.randint(-2, 2)
            num_phrases = max(3, min(50, num_phrases))
            
            self.ngrams_obj = Ngrams(corpus_file="corpora/corpora.pkl", n=self.n_gram, num_phrases=num_phrases, difficulty=self.difficulty.lower())
            test_phrases = self.ngrams_obj.generate_phrases()
            self.target_text = " ".join(phrase for phrase in test_phrases if phrase.strip())
            
            if len(self.target_text) < min_chars:
                extra_needed = min_chars - len(self.target_text)
                extra_phrases = max(3, (extra_needed + approx_chars_per_phrase - 1) // approx_chars_per_phrase)
                tmp = Ngrams(corpus_file="corpora/corpora.pkl", n=self.n_gram, num_phrases=extra_phrases, difficulty=self.difficulty.lower())
                test_phrases += tmp.generate_phrases()
                self.target_text = " ".join(phrase for phrase in test_phrases if phrase.strip())
            
            self.total_chars = len(self.target_text)
            self.state = GAME
            self.typing_text = ""
            self.current_char_index = 0
            self.correct_chars = 0
            self.is_typing = False
            self.time_remaining = float(self.time_limit)
            self.render_start_index = 0
        except Exception as e:
            print(f"Error generating text: {e}")
            self.target_text = "The quick brown fox jumps over the lazy dog. This is a sample text for typing practice."
            self.total_chars = len(self.target_text)
            self.state = GAME
    
    def handle_typing(self, event):
        if event.key == pygame.K_BACKSPACE:
            if self.typing_text:
                self.typing_text = self.typing_text[:-1]
                self.correct_chars = 0
                for i in range(len(self.typing_text)):
                    if i < len(self.target_text) and self.typing_text[i] == self.target_text[i]:
                        self.correct_chars += 1
        elif event.key == pygame.K_RETURN:
            pass
        else:
            if not self.is_typing:
                self.is_typing = True
                self.start_time = time.time()
            char = event.unicode
            if char.isprintable():
                self.typing_text += char
                if len(self.typing_text) <= len(self.target_text):
                    if char == self.target_text[len(self.typing_text) - 1]:
                        self.correct_chars += 1
                        self.create_particles(GAME_WIDTH // 2, GAME_HEIGHT // 2, SUCCESS_GREEN, 8)
                    else:
                        self.create_particles(GAME_WIDTH // 2, GAME_HEIGHT // 2, ERROR_RED, 5)
                remaining_chars = len(self.target_text) - len(self.typing_text)
                if self.is_typing and self.time_remaining > 0.2 and remaining_chars < 150:
                    self.refill_target_text()
                if len(self.typing_text) >= len(self.target_text):
                    if self.is_typing and self.time_remaining > 0.2:
                        self.refill_target_text()
                    else:
                        self.end_game()

    def refill_target_text(self):
        try:
            random.seed()
            
            approx_chars_per_phrase = int(self.base_target_len * (self.avg_word_len + 1)) or 20
            needed_chars = max(200, int(self.time_remaining * 8))
            extra_phrases = max(3, min(40, (needed_chars + approx_chars_per_phrase - 1) // approx_chars_per_phrase))
            
            extra_phrases += random.randint(-1, 2)
            extra_phrases = max(2, min(50, extra_phrases))
            
            generator = Ngrams(corpus_file="corpora/corpora.pkl", n=self.n_gram, num_phrases=extra_phrases, difficulty=self.difficulty.lower())
            more_phrases = generator.generate_phrases()
            extra_text = " ".join(p for p in more_phrases if p.strip())
            if extra_text:
                if self.target_text and not self.target_text.endswith(" "):
                    self.target_text += " "
                self.target_text += extra_text
                self.total_chars = len(self.target_text)
        except Exception as e:
            fallback = " keep typing to improve your speed and accuracy."
            self.target_text += fallback
            self.total_chars = len(self.target_text)
    
    def end_game(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.elapsed_time = min(elapsed, float(self.time_limit))
        else:
            self.elapsed_time = float(self.time_limit)
        elapsed_minutes = self.elapsed_time / 60
        if elapsed_minutes > 0:
            self.wpm = (self.correct_chars / 5) / elapsed_minutes
        else:
            self.wpm = 0
        typed_chars = len(self.typing_text)
        if typed_chars > 0:
            self.accuracy = (self.correct_chars / typed_chars) * 100
        else:
            self.accuracy = 0
        self.state = RESULTS
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == GAME:
                        self.handle_typing(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == MENU:
                        if self.easy_button.is_clicked(event):
                            self.start_game("Easy")
                        elif self.medium_button.is_clicked(event):
                            self.start_game("Medium")
                        elif self.hard_button.is_clicked(event):
                            self.start_game("Hard")
                        elif self.custom_button.is_clicked(event):
                            if self.time_limit == 15:
                                self.time_limit = 30
                            elif self.time_limit == 30:
                                self.time_limit = 60
                            elif self.time_limit == 60:
                                self.time_limit = 120
                            else:
                                self.time_limit = 15
                            self.custom_button.text = f"Time: {self.time_limit}s"
                        elif self.exit_button.is_clicked(event):
                            running = False
                    elif self.state == GAME:
                        if self.restart_button.is_clicked(event):
                            self.start_game(self.difficulty)
                        elif self.menu_button.is_clicked(event):
                            self.state = MENU
                    elif self.state == RESULTS:
                        if self.play_again_button.is_clicked(event):
                            self.start_game(self.difficulty)
                        elif self.back_to_menu_button.is_clicked(event):
                            self.state = MENU
            self.update_particles()
            if self.state == MENU:
                self.draw_menu()
            elif self.state == GAME:
                self.draw_game()
            elif self.state == RESULTS:
                self.draw_results()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

def run_typing_test_with_ngrams(difficulty: str = "medium", time_limit: int = 60):
    try:
        game = TypingGame()
        if difficulty.lower() == "easy":
            game.difficulty = "Easy"
        elif difficulty.lower() == "medium":
            game.difficulty = "Medium"
        elif difficulty.lower() == "hard":
            game.difficulty = "Hard"
        game.time_limit = time_limit
        game.custom_button.text = f"Time: {time_limit}s"
        game.run()
    except Exception as e:
        print(f"Error starting typing test: {e}")
        print("Make sure pygame is installed: pip install pygame")

if __name__ == "__main__":
    game = TypingGame()
    game.run()