import pygame
from pygame.math import Vector2

class Camera:
    """Camera class for handling viewport movement and scaling"""
    def __init__(self, screen_width, screen_height):
        # Initialize camera properties
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.offset = Vector2(0, 0)
        self.speed = 10.0
        self.max_speed = 20.0
        self.min_speed = 5.0
        
        # Movement state
        self.moving = False
        self.drag_start = Vector2(0, 0)
        self.initial_offset = Vector2(0, 0)

    def resize(self, width, height):
        """Handle viewport resize"""
        self.screen_width = width
        self.screen_height = height
        # Adjust camera position if needed
        self.clamp_offset()

    def move(self, dx, dy):
        """Move camera by delta amounts"""
        self.offset.x += dx
        self.offset.y += dy
        self.clamp_offset()

    def set_position(self, x, y):
        """Set absolute camera position"""
        self.offset.x = x
        self.offset.y = y
        self.clamp_offset()

    def clamp_offset(self):
        """Prevent camera from moving too far from the scene"""
        # Define boundaries (adjust these values based on your game world)
        max_x = 5000  # Maximum x coordinate
        min_x = -5000  # Minimum x coordinate
        max_y = 2000  # Maximum y coordinate
        min_y = -2000  # Minimum y coordinate

        self.offset.x = max(min(self.offset.x, max_x), min_x)
        self.offset.y = max(min(self.offset.y, max_y), min_y)

    def handle_event(self, event, menu_visible):
        """Handle camera-related input events"""
        if menu_visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right mouse button
                self.moving = True
                self.drag_start = Vector2(event.pos)
                self.initial_offset = Vector2(self.offset)
                return True
            elif event.button == 4:  # Mouse wheel up
                self.speed = min(self.speed + 1, self.max_speed)
                return True
            elif event.button == 5:  # Mouse wheel down
                self.speed = max(self.speed - 1, self.min_speed)
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Right mouse button
                self.moving = False
                return True

        elif event.type == pygame.MOUSEMOTION and self.moving:
            current_pos = Vector2(event.pos)
            delta = current_pos - self.drag_start
            self.offset = self.initial_offset - delta
            self.clamp_offset()
            return True

        return False

    def get_position(self):
        """Get current camera position"""
        return Vector2(self.offset)

    def screen_to_world(self, screen_pos):
        """Convert screen coordinates to world coordinates"""
        return Vector2(screen_pos) + self.offset

    def world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates"""
        return Vector2(world_pos) - self.offset