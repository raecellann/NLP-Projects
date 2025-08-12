import pygame
from typing import List, Tuple


class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 bg_color: Tuple[int, int, int], fg_color: Tuple[int, int, int],
                 border_color: Tuple[int, int, int] = None, border_width: int = 1,
                 radius: int = 6):
        self.rect = rect
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border_color = border_color
        self.border_width = border_width
        self.radius = radius
        self.active = False

    def draw(self, surface: pygame.Surface):
        bg = self.bg_color
        if self.active:
            # Highlighted state matches web design (#e2b714 on dark background)
            bg = (226, 183, 20)
        pygame.draw.rect(surface, bg, self.rect, border_radius=self.radius)
        if self.border_color:
            pygame.draw.rect(surface, self.border_color, self.rect, width=self.border_width, border_radius=self.radius)
        label = self.font.render(self.text, True, self.fg_color if not self.active else (30, 30, 30))
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class InputField:
    def __init__(self, rect: pygame.Rect, font: pygame.font.Font, placeholder: str = "Start here"):
        self.rect = rect
        self.font = font
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def draw(self, surface: pygame.Surface, colors):
        # Draw background
        pygame.draw.rect(surface, colors['panel'], self.rect, border_radius=8)
        pygame.draw.rect(surface, colors['border'], self.rect, width=2, border_radius=8)

        # Determine text to display
        display_text = self.text if self.text else self.placeholder
        color = colors['text'] if self.text else colors['muted']

        # Render text
        text_surf = self.font.render(display_text, True, color)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 12, self.rect.centery))
        surface.blit(text_surf, text_rect)

        # Draw cursor if active and visible
        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            cursor_rect = pygame.Rect(cursor_x, self.rect.y + 8, 2, self.rect.height - 16)
            pygame.draw.rect(surface, colors['accent'], cursor_rect)

    def handle_event(self, event: pygame.event.Event) -> str:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return ""

        if not self.active:
            return ""

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return ""
            elif event.key == pygame.K_SPACE:
                # Return the current word when space is pressed
                current_word = self.text.strip()
                self.text = ""
                return current_word if current_word else " "
            elif event.key == pygame.K_RETURN:
                # Return the current word when enter is pressed
                current_word = self.text.strip()
                self.text = ""
                return current_word if current_word else " "
            elif event.unicode and event.unicode.isprintable():
                self.text += event.unicode
                return ""
        return ""

    def update_cursor(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:  # Blink every 0.5 seconds
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def clear(self):
        self.text = ""

    def get_text(self) -> str:
        return self.text


class TypingInterface:
    def __init__(self, width: int, height: int):
        # Colors (matching style.css theme)
        self.colors = {
            'bg': (44, 46, 49),
            'panel': (30, 30, 30),
            'border': (58, 58, 58),
            'text': (209, 208, 192),
            'accent': (226, 183, 20),  # #e2b714
            'good': (126, 198, 153),   # #7ec699
            'bad': (232, 92, 81),      # #e85c51
            'muted': (138, 138, 138)
        }

        # Fonts
        self.font_small = pygame.font.SysFont('JetBrains Mono', 16)
        self.font_normal = pygame.font.SysFont('JetBrains Mono', 20)
        self.font_large = pygame.font.SysFont('JetBrains Mono', 28)
        self.font_title = pygame.font.SysFont('JetBrains Mono', 32, bold=True)

        # Layout rects
        self.header_rect = pygame.Rect(0, 0, width, 60)
        self.config_rect = pygame.Rect(0, self.header_rect.bottom, width, 60)
        self.main_rect = pygame.Rect(0, self.config_rect.bottom, width, height - self.config_rect.bottom)

        # UI components
        self._build_ui()
        self._resize_layout(width, height)

    def _build_ui(self):
        # Time buttons
        btn_w = 70
        btn_h = 36
        gap = 10
        start_x = 24
        y = self.config_rect.y + (self.config_rect.height - btn_h) // 2
        times = [15, 30, 60, 120]
        self.time_buttons: List[Button] = []
        for i, t in enumerate(times):
            rect = pygame.Rect(start_x + i * (btn_w + gap), y, btn_w, btn_h)
            btn = Button(rect, str(t), self.font_normal, (0, 0, 0, 0), self.colors['text'], self.colors['border'])
            btn.active = (t == 60)  # Default to 60 seconds
            self.time_buttons.append(btn)

        # Results buttons
        self.new_test_button = Button(
            pygame.Rect(self.header_rect.width - 240, self.header_rect.centery - 18, 100, 36),
            'New Test', self.font_normal, self.colors['accent'], (30, 30, 30), None
        )
        self.reset_button = Button(
            pygame.Rect(self.header_rect.width - 120, self.header_rect.centery - 18, 100, 36),
            'Reset', self.font_normal, self.colors['panel'], self.colors['text'], self.colors['border']
        )

        # Input field
        self.input_field = InputField(pygame.Rect(0, 0, 100, 48), self.font_normal, "Type here to start...")

    def _resize_layout(self, width: int, height: int):
        # Recompute primary layout rects
        self.header_rect = pygame.Rect(0, 0, width, 60)
        self.config_rect = pygame.Rect(0, self.header_rect.bottom, width, 60)
        self.main_rect = pygame.Rect(0, self.config_rect.bottom, width, height - self.config_rect.bottom)

        # Reposition buttons (time options)
        btn_w = 70
        btn_h = 36
        gap = 10
        start_x = 24
        y = self.config_rect.y + (self.config_rect.height - btn_h) // 2
        times = [15, 30, 60, 120]
        for i, (btn, t) in enumerate(zip(self.time_buttons, times)):
            btn.rect.update(start_x + i * (btn_w + gap), y, btn_w, btn_h)

        # Reposition header action buttons
        self.new_test_button.rect.update(self.header_rect.width - 240, self.header_rect.centery - 18, 100, 36)
        self.reset_button.rect.update(self.header_rect.width - 120, self.header_rect.centery - 18, 100, 36)

        # Recompute content rects
        stats_w = min(540, self.main_rect.width - 80)
        stats_h = 90
        stats_x = (self.main_rect.width - stats_w) // 2
        stats_y = self.main_rect.y + 20
        self.live_stats_rect = pygame.Rect(stats_x, stats_y, stats_w, stats_h)

        area_w = min(820, self.main_rect.width - 80)
        area_h = 180
        area_x = (self.main_rect.width - area_w) // 2
        area_y = self.live_stats_rect.bottom + 20
        self.text_area_rect = pygame.Rect(area_x, area_y, area_w, area_h)

        input_h = 48
        self.input_field.rect = pygame.Rect(area_x, self.text_area_rect.bottom + 20, area_w, input_h)

    def draw_header(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.colors['panel'], self.header_rect)
        pygame.draw.line(surface, self.colors['border'], (0, self.header_rect.bottom - 1), 
                        (self.header_rect.width, self.header_rect.bottom - 1))

        # Logo
        logo_text = self.font_title.render('monkeytype', True, self.colors['text'])
        logo_icon = self.font_title.render('🐒', True, self.colors['text'])
        surface.blit(logo_icon, (24, self.header_rect.centery - logo_icon.get_height() // 2))
        surface.blit(logo_text, (64, self.header_rect.centery - logo_text.get_height() // 2))

        # User stub
        user = self.font_normal.render('user_01', True, self.colors['text'])
        surface.blit(user, (self.header_rect.width - 320, self.header_rect.centery - user.get_height() // 2))

        # Action buttons
        self.new_test_button.draw(surface)
        self.reset_button.draw(surface)

    def draw_config(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.colors['panel'], self.config_rect)
        pygame.draw.line(surface, self.colors['border'], (0, self.config_rect.bottom - 1), 
                        (self.config_rect.width, self.config_rect.bottom - 1))

        for btn in self.time_buttons:
            btn.draw(surface)

        # Language selector (static)
        lang_label = self.font_normal.render('🌐  english', True, self.colors['text'])
        surface.blit(lang_label, (self.config_rect.width - 180, self.config_rect.centery - lang_label.get_height() // 2))

    def draw_live_stats(self, surface: pygame.Surface, is_active: bool, elapsed: float, 
                       remaining: float, wpm: int, accuracy: int):
        if not is_active:
            return

        pygame.draw.rect(surface, self.colors['panel'], self.live_stats_rect, border_radius=8)
        pygame.draw.rect(surface, self.colors['border'], self.live_stats_rect, width=1, border_radius=8)

        # Grid: time | wpm | accuracy
        cell_w = self.live_stats_rect.width // 3
        labels = ['time', 'wpm', 'accuracy']
        values = [
            f"{int(remaining//60):02d}:{int(remaining%60):02d}",
            str(wpm),
            f"{accuracy}%",
        ]
        for i in range(3):
            cell_rect = pygame.Rect(self.live_stats_rect.x + i * cell_w, self.live_stats_rect.y, 
                                   cell_w, self.live_stats_rect.height)
            # Label
            label_surf = self.font_small.render(labels[i], True, self.colors['muted'])
            surface.blit(label_surf, (cell_rect.centerx - label_surf.get_width() // 2, cell_rect.y + 10))
            # Value
            value_surf = self.font_large.render(values[i], True, self.colors['accent'])
            surface.blit(value_surf, (cell_rect.centerx - value_surf.get_width() // 2, cell_rect.y + 40))

    def draw_text_area(self, surface: pygame.Surface, words: List[str], current_word_index: int, 
                      typed_words: List[str], is_active: bool):
        # Always draw the text area background
        pygame.draw.rect(surface, self.colors['panel'], self.text_area_rect, border_radius=8)
        pygame.draw.rect(surface, self.colors['border'], self.text_area_rect, width=1, border_radius=8)

        # If no words to display, show a placeholder
        if not words:
            placeholder_text = self.font_large.render("Loading text...", True, self.colors['muted'])
            placeholder_rect = placeholder_text.get_rect(center=self.text_area_rect.center)
            surface.blit(placeholder_text, placeholder_rect)
            return

        # Flow layout of words with highlighting
        x = self.text_area_rect.x + 16
        y = self.text_area_rect.y + 16
        max_w = self.text_area_rect.width - 32
        line_h = self.font_large.get_height() + 8

        for idx, word in enumerate(words):
            word_surf = self.font_large.render(word, True, self.colors['text'])
            word_w = word_surf.get_width() + 12  # spacing
            if x + word_w > self.text_area_rect.x + max_w:
                x = self.text_area_rect.x + 16
                y += line_h

            # Background for current word (only when test is active)
            if is_active and idx == current_word_index:
                bg_rect = pygame.Rect(x - 4, y - 2, word_surf.get_width() + 8, word_surf.get_height() + 4)
                pygame.draw.rect(surface, self.colors['accent'], bg_rect, border_radius=4)
                word_color = (30, 30, 30)
            elif is_active and idx < len(typed_words):
                correct = typed_words[idx] == words[idx]
                word_color = self.colors['good'] if correct else self.colors['bad']
            else:
                # When not active, show all words in normal text color
                word_color = self.colors['text']

            word_surf = self.font_large.render(word, True, word_color)
            surface.blit(word_surf, (x, y))
            x += word_surf.get_width() + 12

    def draw_input(self, surface: pygame.Surface, is_active: bool):
        # Always draw the input field, but show different states
        self.input_field.draw(surface, self.colors)
        
        # If test is not active, show a more prominent hint
        if not is_active:
            # Show a more visible hint that user can click to start
            hint_text = self.font_normal.render("Click here or start typing to begin", True, self.colors['accent'])
            hint_rect = hint_text.get_rect(centerx=self.input_field.rect.centerx, 
                                         top=self.input_field.rect.bottom + 12)
            surface.blit(hint_text, hint_rect)

    def draw_results_panel(self, surface: pygame.Surface, is_active: bool, test_started: bool, 
                          results: dict):
        if is_active or not test_started:
            return

        # Dynamically compute a compact results panel near the top, below config
        panel_w = min(600, self.main_rect.width - 80)
        panel_h = 220
        panel_x = (self.main_rect.width - panel_w) // 2
        panel_y = self.config_rect.bottom + 20  # reduce empty space
        results_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        pygame.draw.rect(surface, self.colors['panel'], results_rect, border_radius=12)
        pygame.draw.rect(surface, self.colors['border'], results_rect, width=1, border_radius=12)

        header = self.font_large.render('Test Complete', True, self.colors['accent'])
        surface.blit(header, (results_rect.centerx - header.get_width() // 2, results_rect.y + 16))

        # Grid 2x2
        labels = ['wpm', 'accuracy', 'time', 'words']
        values = [
            str(results['wpm']),
            f"{results['accuracy']}%",
            f"{int(results['time_taken'])}s",
            str(results['word_count']),
        ]
        grid_x = results_rect.x + 40
        grid_y = results_rect.y + 70
        col_w = (results_rect.width - 80) // 2
        row_h = 60
        for i in range(4):
            cx = grid_x + (i % 2) * col_w
            cy = grid_y + (i // 2) * row_h
            label = self.font_small.render(labels[i], True, self.colors['muted'])
            val = self.font_title.render(values[i], True, self.colors['accent'])
            surface.blit(label, (cx, cy))
            surface.blit(val, (cx, cy + 18))

        # Draw action buttons again for convenience
        self.new_test_button.draw(surface)
        self.reset_button.draw(surface)

    def handle_events(self, events: List[pygame.event.Event]) -> dict:
        result = {
            'time_button_clicked': None,
            'new_test_clicked': False,
            'reset_clicked': False,
            'input_text': ""
        }

        for event in events:
            # Handle time buttons
            for btn, t in zip(self.time_buttons, [15, 30, 60, 120]):
                if btn.handle_event(event):
                    result['time_button_clicked'] = t
                    break

            # Handle action buttons
            if self.new_test_button.handle_event(event):
                result['new_test_clicked'] = True
            elif self.reset_button.handle_event(event):
                result['reset_clicked'] = True

            # Handle input field
            input_result = self.input_field.handle_event(event)
            if input_result:
                result['input_text'] = input_result

        return result

    def update(self, dt: float):
        self.input_field.update_cursor(dt)

    def resize(self, width: int, height: int):
        self._resize_layout(width, height)

    def set_time_button_active(self, duration: int):
        for btn, t in zip(self.time_buttons, [15, 30, 60, 120]):
            btn.active = (t == duration)

    def clear_input(self):
        self.input_field.clear()

    def get_input_text(self) -> str:
        return self.input_field.get_text()

    def activate_input_field(self):
        """Activate the input field for typing"""
        self.input_field.active = True

    def deactivate_input_field(self):
        """Deactivate the input field"""
        self.input_field.active = False
