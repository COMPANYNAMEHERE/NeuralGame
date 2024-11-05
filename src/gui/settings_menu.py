import pygame
from config.settings import Settings

class SettingsMenu:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.visible = False
        self.screen_width = settings.get('screen_width')
        self.screen_height = settings.get('screen_height')
        self.init_dimensions()
        self.init_colors()
        self.init_fonts()
        self.tabs = [
            {"name": "Learning", "controls": []},
            {"name": "Physics", "controls": []},
            {"name": "Training", "controls": []},
            {"name": "Display", "controls": []}
        ]
        self.active_tab = 0
        self.dragging = None
        self.hovered_tab = None
        self.create_controls()
        self.update_control_positions()

    def init_dimensions(self):
        self.width = min(int(self.screen_width * 0.6), 700)
        self.height = min(int(self.screen_height * 0.7), 500)
        self.pos = ((self.screen_width - self.width) // 2, (self.screen_height - self.height) // 2)
        self.padding = int(self.width * 0.04)
        self.slider_width = int(self.width * 0.65)
        self.tab_height = int(self.height * 0.08)
        self.content_y_start = self.tab_height + int(self.height * 0.05)
        self.control_spacing = int(self.height * 0.11)
        self.corner_radius = 6
        self.slider_height = 6
        self.handle_width = max(int(self.width * 0.02), 12)
        self.handle_height = max(int(self.height * 0.04), 20)

    def init_colors(self):
        self.colors = {
            'bg': (245, 245, 245),
            'text': (40, 40, 40),
            'text_light': (255, 255, 255),
            'shadow': (180, 180, 180),
            'border': (180, 180, 180),
            'tab': {
                'active': (245, 245, 245),
                'inactive': (220, 220, 220),
                'hover': (235, 235, 235)
            },
            'slider': {
                'track': (220, 220, 220),
                'fill': (130, 150, 230),
                'handle': (80, 110, 220),
                'handle_hover': (100, 130, 240)
            },
            'toggle': {
                'on': (130, 150, 230),
                'off': (200, 200, 200),
                'border': (100, 120, 200)
            }
        }

    def init_fonts(self):
        base_font_size = min(int(self.height * 0.035), 24)
        self.font = pygame.font.SysFont(None, base_font_size)
        self.title_font = pygame.font.SysFont(None, int(base_font_size * 1.2))

    def create_controls(self):
        self.tabs[0]["controls"] = [
            self.create_slider("Learning Rate", 0.0001, 0.01, self.settings.get('learning_rate'), 4),
            self.create_slider("Hidden Size", 32, 512, float(self.settings.get('hidden_size')), 0),
            self.create_slider("Mutation Rate", 0.01, 0.5, self.settings.get('mutation_rate'), 4)
        ]
        self.tabs[1]["controls"] = [
            self.create_slider("Gravity", 100.0, 2000.0, self.settings.get('gravity'), 1),
            self.create_slider("Max Torque", 1000.0, 100000.0, self.settings.get('max_torque'), 1),
            self.create_slider("Max Motor Velocity", 1.0, 20.0, self.settings.get('max_motor_velocity'), 1)
        ]
        self.tabs[2]["controls"] = [
            self.create_slider("Batch Size", 8, 128, float(self.settings.get('batch_size')), 0),
            self.create_slider("Iteration Time", 10, 120, float(self.settings.get('iteration_time')), 0)
        ]
        self.tabs[3]["controls"] = [
            self.create_toggle("Enable Transparency", self.settings.get('enable_transparency'))
        ]

    def create_slider(self, label, min_val, max_val, current_val, decimal_places):
        value_str = f"{current_val:.{decimal_places}f}" if decimal_places > 0 else str(int(current_val))
        return {
            "type": "slider",
            "label": label,
            "min": min_val,
            "max": max_val,
            "value": current_val,
            "decimal_places": decimal_places,
            "rect": pygame.Rect(self.padding, 0, self.slider_width, self.slider_height),
            "handle_rect": pygame.Rect(0, 0, self.handle_width, self.handle_height),
            "text": f"{label}: {value_str}",
            "active": False,
            "hovered": False
        }

    def create_toggle(self, label, value):
        return {
            "type": "toggle",
            "label": label,
            "value": value,
            "rect": pygame.Rect(
                self.padding,
                0,
                min(int(self.width * 0.2), 140),
                max(int(self.height * 0.06), 32)
            ),
            "text": "On" if value else "Off",
            "hovered": False
        }

    def update_control_positions(self):
        for tab in self.tabs:
            current_y = self.content_y_start
            for control in tab["controls"]:
                control["rect"].y = current_y
                if control["type"] == "slider":
                    handle_x = (control["rect"].x +
                              (control["rect"].width *
                               (control["value"] - control["min"]) /
                               (control["max"] - control["min"])))
                    control["handle_rect"].centerx = handle_x
                    control["handle_rect"].centery = control["rect"].centery
                current_y += self.control_spacing

    def update(self):
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # If mouse button is not pressed, release any dragging
        if not mouse_buttons[0]:
            if self.dragging:
                self.dragging["active"] = False
                self.dragging = None
            return

        # Update hover states and handle dragging
        for control in self.tabs[self.active_tab]["controls"]:
            control_rect = control["rect"].copy()
            control_rect.x += self.pos[0]
            control_rect.y += self.pos[1]
            
            if control["type"] == "slider":
                handle_rect = control["handle_rect"].copy()
                handle_rect.x += self.pos[0]
                handle_rect.y += self.pos[1]
                control["hovered"] = handle_rect.collidepoint(mouse_pos)

                if self.dragging == control:
                    self.update_slider_value(mouse_pos[0], control)
                    self.update_control_positions()
            else:
                control["hovered"] = control_rect.collidepoint(mouse_pos)

    def draw(self, screen):
        if not self.visible:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        shadow_rect = pygame.Rect(self.pos[0] + 3, self.pos[1] + 3, self.width, self.height)
        pygame.draw.rect(screen, self.colors['shadow'], shadow_rect)
        menu_rect = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        pygame.draw.rect(screen, self.colors['bg'], menu_rect)
        pygame.draw.rect(screen, self.colors['border'], menu_rect, 2)
        self.draw_tabs(screen, mouse_pos)
        self.draw_controls(screen, mouse_pos)
        self.draw_close_button(screen, mouse_pos)

    def draw_tabs(self, screen, mouse_pos):
        tab_width = self.width // len(self.tabs)
        for i, tab in enumerate(self.tabs):
            tab_rect = pygame.Rect(self.pos[0] + (i * tab_width), self.pos[1], tab_width, self.tab_height)
            color = (self.colors['tab']['active'] if i == self.active_tab else
                    (self.colors['tab']['hover'] if tab_rect.collidepoint(mouse_pos) else
                     self.colors['tab']['inactive']))
            pygame.draw.rect(screen, color, tab_rect)
            if i < len(self.tabs) - 1:
                pygame.draw.line(screen, self.colors['border'],
                               (tab_rect.right, tab_rect.top),
                               (tab_rect.right, tab_rect.bottom))
            text = self.font.render(tab["name"], True, self.colors['text'])
            text_rect = text.get_rect(center=tab_rect.center)
            screen.blit(text, text_rect)

    def draw_controls(self, screen, mouse_pos):
        active_tab = self.tabs[self.active_tab]
        for control in active_tab["controls"]:
            control_rect = control["rect"].copy()
            control_rect.x += self.pos[0]
            control_rect.y += self.pos[1]
            
            if control["type"] == "slider":
                self.draw_slider(screen, control, control_rect)
            elif control["type"] == "toggle":
                self.draw_toggle(screen, control, control_rect)

    def draw_slider(self, screen, control, slider_rect):
        label = self.font.render(control["text"], True, self.colors['text'])
        screen.blit(label, (slider_rect.x, slider_rect.y - 25))
        pygame.draw.rect(screen, self.colors['slider']['track'], slider_rect, 0, 3)
        value_ratio = (control["value"] - control["min"]) / (control["max"] - control["min"])
        filled_rect = slider_rect.copy()
        filled_rect.width = max(6, filled_rect.width * value_ratio)
        pygame.draw.rect(screen, self.colors['slider']['fill'], filled_rect, 0, 3)
        handle_x = slider_rect.x + (slider_rect.width * value_ratio)
        handle_rect = control["handle_rect"].copy()
        handle_rect.centerx, handle_rect.centery = handle_x, slider_rect.centery
        handle_color = (self.colors['slider']['handle'] if control.get("active")
                       else self.colors['slider']['handle_hover'])
        pygame.draw.rect(screen, handle_color, handle_rect, 0, 4)
        pygame.draw.rect(screen, self.colors['border'], handle_rect, 2, 4)

    def draw_toggle(self, screen, control, toggle_rect):
        label = self.font.render(control["label"], True, self.colors['text'])
        screen.blit(label, (toggle_rect.x, toggle_rect.y - 25))
        color = self.colors['toggle']['on'] if control["value"] else self.colors['toggle']['off']
        pygame.draw.rect(screen, color, toggle_rect, 0, 6)
        pygame.draw.rect(screen, self.colors['toggle']['border'], toggle_rect, 2, 6)
        text = self.font.render(control["text"], True,
                              self.colors['text_light'] if control["value"] else self.colors['text'])
        text_rect = text.get_rect(center=toggle_rect.center)
        screen.blit(text, text_rect)

    def draw_close_button(self, screen, mouse_pos):
        close_size = (min(int(self.width * 0.15), 90), min(int(self.height * 0.08), 36))
        close_rect = pygame.Rect(self.pos[0] + self.width - close_size[0] - self.padding,
                               self.pos[1] + self.height - close_size[1] - self.padding, *close_size)
        color = tuple(min(c + 20, 255) for c in self.colors['toggle']['on']) if close_rect.collidepoint(mouse_pos) else self.colors['toggle']['on']
        pygame.draw.rect(screen, color, close_rect, 0, 6)
        pygame.draw.rect(screen, self.colors['toggle']['border'], close_rect, 2, 6)
        close_text = self.font.render("Close", True, self.colors['text_light'])
        text_rect = close_text.get_rect(center=close_rect.center)
        screen.blit(close_text, text_rect)

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            was_dragging = self.dragging is not None
            if self.dragging:
                self.dragging["active"] = False
                self.dragging = None
            return was_dragging
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_slider_value(event.pos[0], self.dragging)
            return True

        return False

    def handle_mouse_down(self, mouse_pos):
        tab_width = self.width // len(self.tabs)
        for i in range(len(self.tabs)):
            tab_rect = pygame.Rect(self.pos[0] + (i * tab_width), self.pos[1], tab_width, self.tab_height)
            if tab_rect.collidepoint(mouse_pos):
                self.active_tab = i
                return True

        close_size = (min(int(self.width * 0.15), 90), min(int(self.height * 0.08), 36))
        close_rect = pygame.Rect(self.pos[0] + self.width - close_size[0] - self.padding,
                               self.pos[1] + self.height - close_size[1] - self.padding, *close_size)
        if close_rect.collidepoint(mouse_pos):
            self.visible = False
            return True

        for control in self.tabs[self.active_tab]["controls"]:
            if control["type"] == "slider":
                handle_rect = control["handle_rect"].copy()
                handle_rect.x += self.pos[0]
                handle_rect.y += self.pos[1]
                slider_rect = control["rect"].copy()
                slider_rect.x += self.pos[0]
                slider_rect.y += self.pos[1]
                
                if handle_rect.collidepoint(mouse_pos) or slider_rect.collidepoint(mouse_pos):
                    control["active"] = True
                    self.dragging = control
                    self.update_slider_value(mouse_pos[0], control)
                    self.update_control_positions()
                    return True
            elif control["type"] == "toggle":
                control_rect = control["rect"].copy()
                control_rect.x += self.pos[0]
                control_rect.y += self.pos[1]
                if control_rect.collidepoint(mouse_pos):
                    self.toggle_value(control)
                    return True
                return False

    def update_slider_value(self, mouse_x, control):
        slider_rect = control["rect"].copy()
        slider_rect.x += self.pos[0]
        relative_x = max(0, min(1, (mouse_x - slider_rect.x) / slider_rect.width))
        value_range = control["max"] - control["min"]
        value = round((control["min"] + (value_range * relative_x)) / (value_range / 1000)) * (value_range / 1000)
        value = min(max(value, control["min"]), control["max"])
        control["value"] = value
        value_text = str(int(value)) if control["decimal_places"] == 0 else f"{value:.{control['decimal_places']}f}"
        control["text"] = f"{control['label']}: {value_text}"
        setting_map = {
            "Learning Rate": ('learning_rate', float),
            "Hidden Size": ('hidden_size', int),
            "Mutation Rate": ('mutation_rate', float),
            "Gravity": ('gravity', float),
            "Max Torque": ('max_torque', float),
            "Max Motor Velocity": ('max_motor_velocity', float),
            "Batch Size": ('batch_size', int),
            "Iteration Time": ('iteration_time', int)
        }
        if control["label"] in setting_map:
            key, type_ = setting_map[control["label"]]
            self.settings.set(key, type_(value))

    def toggle_value(self, control):
        control["value"] = not control["value"]
        control["text"] = "On" if control["value"] else "Off"
        if control["label"] == "Enable Transparency":
            self.settings.set('enable_transparency', control["value"])

    def toggle(self):
        self.visible = not self.visible

    def resize(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.init_dimensions()
        self.init_fonts()
        self.create_controls()
        self.update_control_positions()