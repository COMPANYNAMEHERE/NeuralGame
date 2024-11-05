# src/gui/gui.py

import pygame
from gui.settings_menu import SettingsMenu

class GUI:
    def __init__(self, settings, screen):
        """
        Initialize the GUI with settings and the Pygame screen.

        :param settings: Instance of the Settings class.
        :param screen: The Pygame screen surface.
        """
        self.settings = settings
        self.screen = screen
        self.screen_width = settings.get('screen_width')
        self.screen_height = settings.get('screen_height')
        self.pause_requested = None
        self.stop_requested = False
        self.load_requested = False
        self.interacting = False
        
        # Initialize constants and scaling factors
        self.init_dimensions()
        
        # Initialize UI elements
        self.font = pygame.font.SysFont(None, self.font_size)
        self.settings_menu = SettingsMenu(settings, screen)  # Pass screen to SettingsMenu
        self.buttons = []
        self.create_buttons()
        
        # Button colors
        self.colors = {
            'active': (130, 150, 230),
            'inactive': (220, 220, 220),
            'hover': (200, 210, 240),
            'border': (180, 180, 180),
            'text': (40, 40, 40),
            'text_active': (255, 255, 255)
        }

    def init_dimensions(self):
        """Initialize responsive dimensions based on screen size."""
        base_size = min(self.screen_width, self.screen_height)
        self.margin = max(int(base_size * 0.02), 10)
        self.button_width = min(max(int(self.screen_width * 0.1), 100), 120)
        self.button_height = min(max(int(self.screen_height * 0.05), 30), 36)
        self.button_spacing = int(self.button_height * 1.2)
        self.font_size = min(max(int(base_size * 0.02), 18), 24)
        self.corner_radius = 6

    def create_buttons(self):
        """Create button configurations with improved layout."""
        button_configs = [
            {
                "text": "Start",
                "action": self.start_simulation,
                "tooltip": "Start the simulation"
            },
            {
                "text": "Pause",
                "action": self.pause_simulation,
                "tooltip": "Pause/Resume the simulation"
            },
            {
                "text": "Stop",
                "action": self.stop_simulation,
                "tooltip": "Stop and reset the simulation"
            },
            {
                "text": "Load",
                "action": self.load_generation,
                "tooltip": "Load a saved generation"
            },
            {
                "text": "Settings",
                "action": self.toggle_settings,
                "tooltip": "Open settings menu"
            }
        ]

        self.buttons = []
        button_y = self.margin

        for config in button_configs:
            button = {
                "text": config["text"],
                "action": config["action"],
                "tooltip": config["tooltip"],
                "rect": pygame.Rect(
                    self.margin,
                    button_y,
                    self.button_width,
                    self.button_height
                ),
                "hovered": False
            }
            self.buttons.append(button)
            button_y += self.button_spacing

    def resize(self, screen_width, screen_height):
        """
        Handle window resize events.

        :param screen_width: New width of the screen.
        :param screen_height: New height of the screen.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode(
            (screen_width, screen_height),
            pygame.RESIZABLE
        )
        self.init_dimensions()
        self.font = pygame.font.SysFont(None, self.font_size)
        self.create_buttons()
        self.settings_menu.resize(screen_width, screen_height)

    def draw(self, screen):
        """
        Draw GUI elements with improved visual styling.

        :param screen: The Pygame screen surface.
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw buttons
        for button in self.buttons:
            # Update hover state
            button["hovered"] = button["rect"].collidepoint(mouse_pos)
            
            # Determine button color
            if button["text"] == "Start" and self.settings.get('running'):
                color = self.colors['active']
                text_color = self.colors['text_active']
            elif button["text"] == "Pause" and self.pause_requested:
                color = self.colors['active']
                text_color = self.colors['text_active']
            else:
                color = self.colors['hover'] if button["hovered"] else self.colors['inactive']
                text_color = self.colors['text']

            # Draw button background with shadow
            shadow_rect = button["rect"].copy()
            shadow_rect.move_ip(2, 2)
            pygame.draw.rect(screen, (160, 160, 160), shadow_rect, 0, self.corner_radius)
            
            # Draw main button
            pygame.draw.rect(screen, color, button["rect"], 0, self.corner_radius)
            pygame.draw.rect(screen, self.colors['border'], button["rect"], 2, self.corner_radius)

            # Draw button text
            text_surf = self.font.render(button["text"], True, text_color)
            text_rect = text_surf.get_rect(center=button["rect"].center)
            screen.blit(text_surf, text_rect)

            # Draw tooltip if hovered
            if button["hovered"]:
                tooltip_text = self.font.render(button["tooltip"], True, self.colors['text'])
                tooltip_rect = tooltip_text.get_rect()
                tooltip_rect.midleft = (button["rect"].right + 10, button["rect"].centery)
                
                # Draw tooltip background
                padding = 5
                bg_rect = tooltip_rect.inflate(padding * 2, padding * 2)
                pygame.draw.rect(screen, (245, 245, 245), bg_rect, 0, 3)
                pygame.draw.rect(screen, self.colors['border'], bg_rect, 1, 3)
                screen.blit(tooltip_text, tooltip_rect)

        # Draw settings menu if visible
        if self.settings_menu.visible:
            self.settings_menu.draw(screen)

    def handle_event(self, event):
        """
        Handle input events.

        :param event: The Pygame event to handle.
        :return: True if the event was handled by the GUI, False otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Handle settings menu events first if visible
            if self.settings_menu.visible:
                if self.settings_menu.handle_event(event):
                    return True
            
            # Handle button clicks
            for button in self.buttons:
                if button["rect"].collidepoint(mouse_pos):
                    button["action"]()
                    self.interacting = True
                    return True
        
        return False

    def update(self, time_delta):
        """
        Update GUI state.

        :param time_delta: Time elapsed since the last frame.
        """
        if self.settings_menu.visible:
            self.settings_menu.update()

    def is_interacting(self):
        """
        Check if GUI is being interacted with.

        :return: True if interacting with GUI, False otherwise.
        """
        return self.interacting or self.settings_menu.visible

    # Button action methods
    def start_simulation(self):
        """Start the simulation."""
        self.settings.set('running', True)
        self.pause_requested = False
        self.interacting = False

    def pause_simulation(self):
        """Toggle pause/resume of the simulation."""
        if self.settings.get('running'):
            self.pause_requested = not self.pause_requested
        self.interacting = False

    def stop_simulation(self):
        """Stop and reset the simulation."""
        self.stop_requested = True
        self.interacting = False

    def load_generation(self):
        """Request to load a saved generation."""
        self.load_requested = True
        self.interacting = False

    def toggle_settings(self):
        """Toggle the visibility of the settings menu."""
        self.settings_menu.toggle()
        self.interacting = False
