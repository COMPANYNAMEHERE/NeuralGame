# src/gui/settings_menu.py

import pygame
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog
from src.utils.recorder import ScreenRecorder
from config.settings import Settings

class SettingsMenu:
    def __init__(self, settings: Settings, screen):
        """
        Initialize the SettingsMenu with settings and the Pygame screen.

        :param settings: Instance of the Settings class.
        :param screen: The Pygame screen surface.
        """
        self.settings = settings
        self.screen = screen
        self.screen_width = settings.get('screen_width')
        self.screen_height = settings.get('screen_height')
        self.visible = False
        self.popup = None  # Popup state

        # Initialize dimensions and fonts
        self.init_dimensions()
        self.init_colors()
        self.init_fonts()

        # Initialize tabs and controls
        self.tabs = [
            {"name": "Learning", "controls": []},
            {"name": "Physics", "controls": []},
            {"name": "Training", "controls": []},
            {"name": "Display", "controls": []}
        ]
        self.active_tab = 0
        self.dragging = None

        # Initialize recorder
        self.recorder = None

        # Create controls
        self.create_controls()
        self.update_control_positions()

    def init_dimensions(self):
        """Initialize responsive dimensions based on screen size."""
        self.width = min(int(self.screen_width * 0.6), 700)
        self.height = min(int(self.screen_height * 0.7), 500)
        self.pos = ((self.screen_width - self.width) // 2, (self.screen_height - self.height) // 2)
        self.padding = int(self.width * 0.04)
        self.slider_width = int(self.width * 0.65)
        self.tab_height = int(self.height * 0.08)
        self.content_y_start = self.tab_height + int(self.height * 0.05)
        self.control_spacing = int(self.height * 0.15)  # Increased spacing for clarity
        self.corner_radius = 6
        self.slider_height = 6
        self.handle_width = max(int(self.width * 0.02), 12)
        self.handle_height = max(int(self.height * 0.04), 20)

    def init_colors(self):
        """Initialize color schemes for the settings menu."""
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
            },
            'popup_bg': (50, 50, 50),
            'popup_text': (255, 255, 255),
            'progress_bar_bg': (100, 100, 100),
            'progress_bar_fill': (130, 150, 230),
            'error': (255, 0, 0)
        }

    def init_fonts(self):
        """Initialize fonts based on screen size."""
        base_font_size = min(int(self.height * 0.035), 24)
        self.font = pygame.font.SysFont(None, base_font_size)
        self.title_font = pygame.font.SysFont(None, int(base_font_size * 1.2))
        self.popup_font = pygame.font.SysFont(None, int(base_font_size * 1.1))

    def create_controls(self):
        """Create sliders and toggles for each tab."""
        self.tabs[0]["controls"] = [
            self.create_slider("Learning Rate", 0.0001, 0.01, self.settings.get('learning_rate'), 4),
            self.create_slider("Hidden Size", 32, 512, float(self.settings.get('hidden_size')), 0),
            self.create_slider("Mutation Rate", 0.01, 0.5, self.settings.get('mutation_rate'), 4)
        ]
        self.tabs[1]["controls"] = [
            self.create_slider("Gravity", 0.0, 2000.0, self.settings.get('gravity'), 2),
            self.create_slider("Max Torque", 0.0, 100000.0, self.settings.get('max_torque'), 1),
            self.create_slider("Max Motor Velocity", 0.0, 20.0, self.settings.get('max_motor_velocity'), 1)
        ]
        self.tabs[2]["controls"] = [
            self.create_slider("Batch Size", 8, 128, float(self.settings.get('batch_size')), 0),
            self.create_slider("Iteration Time", 10, 120, float(self.settings.get('iteration_time')), 0)
        ]
        self.tabs[3]["controls"] = [
            self.create_toggle("Enable Transparency", self.settings.get('enable_transparency')),
            self.create_toggle("Enable Recording", self.settings.get('enable_recording')),
            self.create_folder_selector("Video Output Folder", self.settings.get('video_output_folder'))
        ]

    def create_slider(self, label, min_val, max_val, current_val, decimal_places):
        """Create a slider control."""
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
        """Create a toggle control."""
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

    def create_folder_selector(self, label, current_folder):
        """Create a folder selector control."""
        return {
            "type": "folder_selector",
            "label": label,
            "current_folder": current_folder,
            "rect": pygame.Rect(
                self.padding,
                0,
                min(int(self.width * 0.6), 200),
                max(int(self.height * 0.06), 32)
            ),
            "button_rect": pygame.Rect(0, 0, 80, 32),
            "hovered": False
        }

    def update_control_positions(self):
        """Update the positions of controls within each tab."""
        for tab in self.tabs:
            current_y = self.content_y_start
            for control in tab["controls"]:
                control["rect"].y = current_y
                if control["type"] == "slider":
                    # Set initial handle position based on current value
                    handle_x = (control["rect"].x +
                              (control["rect"].width *
                               (control["value"] - control["min"]) /
                               (control["max"] - control["min"])))
                    control["handle_rect"].centerx = handle_x
                    control["handle_rect"].centery = control["rect"].centery
                elif control["type"] == "folder_selector":
                    # Position the "Browse" button next to the path display
                    control["button_rect"].x = control["rect"].right + 10
                    control["button_rect"].y = control["rect"].y
                current_y += self.control_spacing

    def update(self):
        """Update the settings menu state."""
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # If mouse button is not pressed, release any dragging
        if not mouse_buttons[0]:
            if self.dragging:
                self.dragging["active"] = False
                self.dragging = None

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
            elif control["type"] == "folder_selector":
                # Update hover state for the browse button
                button_rect = control["button_rect"].copy()
                button_rect.x += self.pos[0] + control["rect"].width + 10
                button_rect.y += self.pos[1]
                control["hovered"] = button_rect.collidepoint(mouse_pos)
            else:
                control["hovered"] = control_rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """Render the settings menu and any active popups."""
        if not self.visible:
            return

        # Draw main menu with drop shadow
        mouse_pos = pygame.mouse.get_pos()
        shadow_rect = pygame.Rect(self.pos[0] + 3, self.pos[1] + 3, self.width, self.height)
        pygame.draw.rect(screen, self.colors['shadow'], shadow_rect, border_radius=self.corner_radius)
        menu_rect = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        pygame.draw.rect(screen, self.colors['bg'], menu_rect, border_radius=self.corner_radius)
        pygame.draw.rect(screen, self.colors['border'], menu_rect, 2, border_radius=self.corner_radius)
        self.draw_tabs(screen, mouse_pos)
        self.draw_controls(screen, mouse_pos)
        self.draw_close_button(screen, mouse_pos)

        # Draw popup if active
        if self.popup:
            self.draw_popup(screen)

    def draw_tabs(self, screen, mouse_pos):
        """Draw the tabs for different settings categories."""
        tab_width = self.width // len(self.tabs)
        for i, tab in enumerate(self.tabs):
            tab_rect = pygame.Rect(self.pos[0] + (i * tab_width), self.pos[1], tab_width, self.tab_height)
            color = (self.colors['tab']['active'] if i == self.active_tab else
                    (self.colors['tab']['hover'] if tab_rect.collidepoint(mouse_pos) else
                     self.colors['tab']['inactive']))
            pygame.draw.rect(screen, color, tab_rect, border_radius=0)
            if i < len(self.tabs) - 1:
                pygame.draw.line(screen, self.colors['border'],
                               (tab_rect.right, tab_rect.top),
                               (tab_rect.right, tab_rect.bottom))
            text = self.font.render(tab["name"], True, self.colors['text'])
            text_rect = text.get_rect(center=tab_rect.center)
            screen.blit(text, text_rect)

    def draw_controls(self, screen, mouse_pos):
        """Draw the controls for the active tab."""
        active_tab = self.tabs[self.active_tab]
        for control in active_tab["controls"]:
            control_rect = control["rect"].copy()
            control_rect.x += self.pos[0]
            control_rect.y += self.pos[1]

            if control["type"] == "slider":
                self.draw_slider(screen, control, control_rect)
            elif control["type"] == "toggle":
                self.draw_toggle(screen, control, control_rect)
            elif control["type"] == "folder_selector":
                self.draw_folder_selector(screen, control, control_rect)

    def draw_slider(self, screen, control, slider_rect):
        """Render a slider control."""
        # Draw label above the slider
        label = self.font.render(control["label"], True, self.colors['text'])
        screen.blit(label, (slider_rect.x, slider_rect.y - 30))

        # Draw slider track
        pygame.draw.rect(screen, self.colors['slider']['track'], slider_rect, 0, 3)

        # Calculate filled portion
        value_ratio = (control["value"] - control["min"]) / (control["max"] - control["min"])
        filled_rect = slider_rect.copy()
        filled_rect.width = max(6, int(filled_rect.width * value_ratio))
        pygame.draw.rect(screen, self.colors['slider']['fill'], filled_rect, 0, 3)

        # Draw slider handle
        handle_x = slider_rect.x + int(slider_rect.width * value_ratio)
        handle_rect = control["handle_rect"].copy()
        handle_rect.centerx, handle_rect.centery = handle_x, slider_rect.centery
        handle_color = (self.colors['slider']['handle'] if control.get("active")
                       else self.colors['slider']['handle_hover'])
        pygame.draw.rect(screen, handle_color, handle_rect, 0, 4)
        pygame.draw.rect(screen, self.colors['border'], handle_rect, 2, 4)

        # Draw current value next to the slider
        value_text = f"{control['value']:.{control['decimal_places']}f}" if control["decimal_places"] > 0 else str(int(control["value"]))
        value_surf = self.font.render(value_text, True, self.colors['text'])
        value_rect = value_surf.get_rect(midleft=(slider_rect.right + 10, slider_rect.centery))
        screen.blit(value_surf, value_rect)

    def draw_toggle(self, screen, control, toggle_rect):
        """Render a toggle control."""
        # Draw label above the toggle
        label = self.font.render(control["label"], True, self.colors['text'])
        screen.blit(label, (toggle_rect.x, toggle_rect.y - 30))

        # Draw toggle switch
        color = self.colors['toggle']['on'] if control["value"] else self.colors['toggle']['off']
        pygame.draw.rect(screen, color, toggle_rect, 0, 6)
        pygame.draw.rect(screen, self.colors['toggle']['border'], toggle_rect, 2, 6)

        # Draw toggle state text
        text = self.font.render(control["text"], True,
                              self.colors['text_light'] if control["value"] else self.colors['text'])
        text_rect = text.get_rect(center=toggle_rect.center)
        screen.blit(text, text_rect)

    def draw_folder_selector(self, screen, control, folder_rect):
        """Render a folder selector control."""
        # Draw label above the folder selector
        label = self.font.render(control["label"], True, self.colors['text'])
        screen.blit(label, (folder_rect.x, folder_rect.y - 30))

        # Draw the current folder path inside a box
        path_rect = pygame.Rect(folder_rect.x, folder_rect.y, folder_rect.width - control["button_rect"].width - 20, folder_rect.height)
        pygame.draw.rect(screen, (255, 255, 255), path_rect, 0, 6)
        pygame.draw.rect(screen, self.colors['border'], path_rect, 2, 6)
        folder_text = self.font.render(self.shorten_path(control["current_folder"], path_rect.width - 10), True, self.colors['text'])
        folder_text_rect = folder_text.get_rect(midleft=(path_rect.x + 10, path_rect.centery))
        screen.blit(folder_text, folder_text_rect)

        # Draw the browse button next to the path
        button_rect = control["button_rect"].copy()
        button_rect.x += self.pos[0] + path_rect.width + 10  # Adjusted positioning
        button_rect.y += self.pos[1]
        button_color = self.colors['toggle']['on'] if control["hovered"] else self.colors['toggle']['off']
        pygame.draw.rect(screen, button_color, button_rect, 0, 6)
        pygame.draw.rect(screen, self.colors['toggle']['border'], button_rect, 2, 6)
        button_text = self.font.render("Browse", True, self.colors['text_light'])
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)

    def shorten_path(self, path, max_width):
        """Shorten the folder path to fit within a given width."""
        font = self.font
        text = path
        while font.size(text)[0] > max_width and len(text) > 3:
            text = '...' + text[3:]
        return text

    def draw_close_button(self, screen, mouse_pos):
        """Draw the close button for the settings menu."""
        close_size = (min(int(self.width * 0.15), 90), min(int(self.height * 0.08), 36))
        close_rect = pygame.Rect(self.pos[0] + self.width - close_size[0] - self.padding,
                               self.pos[1] + self.height - close_size[1] - self.padding, *close_size)
        color = tuple(min(c + 20, 255) for c in self.colors['toggle']['on']) if close_rect.collidepoint(mouse_pos) else self.colors['toggle']['on']
        pygame.draw.rect(screen, color, close_rect, 0, 6)
        pygame.draw.rect(screen, self.colors['toggle']['border'], close_rect, 2, 6)
        close_text = self.font.render("Close", True, self.colors['text_light'])
        text_rect = close_text.get_rect(center=close_rect.center)
        screen.blit(close_text, text_rect)

    def draw_popup(self, screen):
        """Render a popup with a message and optional progress bar."""
        # Define popup dimensions
        popup_width = int(self.width * 0.5)
        popup_height = int(self.height * 0.3)
        popup_x = self.pos[0] + (self.width - popup_width) // 2
        popup_y = self.pos[1] + (self.height - popup_height) // 2
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(screen, self.colors['popup_bg'], popup_rect, border_radius=10)
        pygame.draw.rect(screen, self.colors['border'], popup_rect, 2, border_radius=10)

        # Render the message
        message = self.popup['message']
        message_lines = message.split('\n')
        for i, line in enumerate(message_lines):
            text = self.popup_font.render(line, True, self.colors['popup_text'])
            text_rect = text.get_rect(center=(popup_x + popup_width // 2, popup_y + 50 + i * 30))
            screen.blit(text, text_rect)

        # Render progress bar if needed
        if self.popup['type'] == 'saving':
            progress_bar_width = popup_width - 40
            progress_bar_height = 20
            progress_x = popup_x + 20
            progress_y = popup_y + 150
            pygame.draw.rect(screen, self.colors['progress_bar_bg'], (progress_x, progress_y, progress_bar_width, progress_bar_height), border_radius=10)
            # Indeterminate progress bar (animation)
            current_time = pygame.time.get_ticks() // 10
            moving_width = 100
            move_x = (current_time % (progress_bar_width + moving_width)) - moving_width
            pygame.draw.rect(screen, self.colors['progress_bar_fill'], (progress_x + move_x, progress_y, moving_width, progress_bar_height), border_radius=10)

    def handle_event(self, event):
        """
        Handle input events.

        :param event: The Pygame event to handle.
        :return: True if the event was handled by the settings menu, False otherwise.
        """
        if not self.visible:
            return False

        if self.popup:
            # If a popup is active, handle only closing it if needed
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.popup = None
            return True

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
        """Handle mouse button down events."""
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

        active_tab = self.tabs[self.active_tab]
        for control in active_tab["controls"]:
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
            elif control["type"] == "folder_selector":
                folder_rect = control["rect"].copy()
                folder_rect.x += self.pos[0]
                folder_rect.y += self.pos[1]
                button_rect = control["button_rect"].copy()
                button_rect.x += self.pos[0] + folder_rect.width + 10  # Adjusted positioning
                button_rect.y += self.pos[1]
                if button_rect.collidepoint(mouse_pos):
                    self.select_video_output_folder(control)
                    return True

        return False

    def update_slider_value(self, mouse_x, control):
        """Update the value of a slider based on mouse position."""
        slider_rect = control["rect"].copy()
        slider_rect.x += self.pos[0]
        relative_x = max(0, min(1, (mouse_x - slider_rect.x) / slider_rect.width))
        value_range = control["max"] - control["min"]
        value = control["min"] + (value_range * relative_x)
        if control["decimal_places"] > 0:
            value = round(value, control["decimal_places"])
        else:
            value = int(round(value))
        value = min(max(value, control["min"]), control["max"])
        control["value"] = value
        value_text = f"{value:.{control['decimal_places']}f}" if control["decimal_places"] > 0 else str(int(value))
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
        """Toggle the value of a toggle control."""
        control["value"] = not control["value"]
        control["text"] = "On" if control["value"] else "Off"
        if control["label"] == "Enable Transparency":
            self.settings.set('enable_transparency', control["value"])
        elif control["label"] == "Enable Recording":
            self.settings.set('enable_recording', control["value"])
            if control["value"]:
                # Enable Recording: start recording
                if not self.check_ffmpeg_installed():
                    # Show error popup
                    control["value"] = False
                    control["text"] = "Off"
                    self.settings.set('enable_recording', False)
                    self.show_popup("FFmpeg is not installed or not found in PATH.", popup_type='error')
                else:
                    # Show information popup
                    self.show_popup("Recording has been enabled.\n\nThis feature uses FFmpeg to convert screenshots into video.\nEnsure FFmpeg is installed and in your system's PATH.", popup_type='info')
                    # Initialize and start recorder
                    if not self.recorder:
                        video_output_folder = self.settings.get('video_output_folder')
                        self.recorder = ScreenRecorder(self.screen, self.get_screen_size, video_output_folder)
                    self.recorder.start_recording()
            else:
                # Disable Recording: stop recording and convert to video
                if self.recorder:
                    self.show_popup("Saving video...", popup_type='saving')
                    self.recorder.stop_recording(on_complete=self.on_conversion_complete, on_error=self.on_conversion_error)

    def check_ffmpeg_installed(self):
        """Check if FFmpeg is installed and accessible."""
        try:
            result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def show_popup(self, message, popup_type='info'):
        """
        Display a popup with a message.

        :param message: The message to display.
        :param popup_type: Type of popup ('info', 'error', 'saving').
        """
        self.popup = {
            'message': message,
            'type': popup_type
        }

    def on_conversion_complete(self, video_filename):
        """
        Callback when video conversion is complete.

        :param video_filename: Path to the saved video file.
        """
        # Hide saving popup and show success message
        self.popup = None
        self.show_popup(f"Video saved successfully:\n{video_filename}", popup_type='info')
        # Cleanup recorder
        self.recorder = None

    def on_conversion_error(self, error_message):
        """
        Callback when video conversion encounters an error.

        :param error_message: The error message to display.
        """
        # Hide saving popup and show error message
        self.popup = None
        self.show_popup(f"Error during video conversion:\n{error_message}", popup_type='error')
        # Cleanup recorder
        self.recorder = None

    def toggle(self):
        """Toggle the visibility of the settings menu."""
        self.visible = not self.visible

    def resize(self, screen_width, screen_height):
        """
        Handle window resize events.

        :param screen_width: New width of the screen.
        :param screen_height: New height of the screen.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.init_dimensions()
        self.init_fonts()
        self.create_controls()
        self.update_control_positions()

    def get_screen_size(self):
        """Get the current screen size."""
        return self.screen.get_size()

    def draw_popup(self, screen):
        """Render a popup with a message and optional progress bar."""
        # Define popup dimensions
        popup_width = int(self.width * 0.5)
        popup_height = int(self.height * 0.3)
        popup_x = self.pos[0] + (self.width - popup_width) // 2
        popup_y = self.pos[1] + (self.height - popup_height) // 2
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(screen, self.colors['popup_bg'], popup_rect, border_radius=10)
        pygame.draw.rect(screen, self.colors['border'], popup_rect, 2, border_radius=10)

        # Render the message
        message = self.popup['message']
        message_lines = message.split('\n')
        for i, line in enumerate(message_lines):
            text = self.popup_font.render(line, True, self.colors['popup_text'])
            text_rect = text.get_rect(center=(popup_x + popup_width // 2, popup_y + 50 + i * 30))
            screen.blit(text, text_rect)

        # Render progress bar if needed
        if self.popup['type'] == 'saving':
            progress_bar_width = popup_width - 40
            progress_bar_height = 20
            progress_x = popup_x + 20
            progress_y = popup_y + 150
            pygame.draw.rect(screen, self.colors['progress_bar_bg'], (progress_x, progress_y, progress_bar_width, progress_bar_height), border_radius=10)
            # Indeterminate progress bar (animation)
            current_time = pygame.time.get_ticks() // 10
            moving_width = 100
            move_x = (current_time % (progress_bar_width + moving_width)) - moving_width
            pygame.draw.rect(screen, self.colors['progress_bar_fill'], (progress_x + move_x, progress_y, moving_width, progress_bar_height), border_radius=10)

    def select_video_output_folder(self, control):
        """Open a folder dialog to select the video output folder."""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        selected_folder = filedialog.askdirectory(initialdir=self.settings.get('video_output_folder'),
                                                 title="Select Video Output Folder")
        root.destroy()

        if selected_folder:
            # Update the control's current folder display
            control["current_folder"] = selected_folder
            self.settings.set('video_output_folder', selected_folder)
            self.show_popup(f"Video output folder set to:\n{selected_folder}", popup_type='info')
            # If recording is active, update the recorder's output folder
            if self.recorder and self.recorder.recording:
                self.recorder.video_output_folder = selected_folder

# Public Classes
__all__ = ['SettingsMenu']
