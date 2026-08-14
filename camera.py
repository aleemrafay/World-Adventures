"""
camera.py
Handles side-scrolling: offsets everything drawn to keep the player
roughly centered on screen, without scrolling past level boundaries.
"""

import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    def __init__(self, level_width_px, level_height_px):
        self.offset_x = 0
        self.offset_y = 0
        self.level_width_px = level_width_px
        self.level_height_px = level_height_px

    def update(self, target_rect):
        """
        target_rect: the player's pygame.Rect (world coordinates).
        Keeps target roughly centered horizontally; clamps to level edges.
        """
        # Center target horizontally on screen
        desired_x = target_rect.centerx - SCREEN_WIDTH // 2
        desired_y = target_rect.centery - SCREEN_HEIGHT // 2

        # Clamp so camera doesn't show beyond level bounds
        max_x = max(0, self.level_width_px - SCREEN_WIDTH)
        max_y = max(0, self.level_height_px - SCREEN_HEIGHT)

        self.offset_x = max(0, min(desired_x, max_x))
        self.offset_y = max(0, min(desired_y, max_y))

    def apply(self, rect):
        """Return a screen-space rect for drawing, given a world-space rect."""
        return pygame.Rect(
            rect.x - self.offset_x,
            rect.y - self.offset_y,
            rect.width,
            rect.height
        )

    def apply_pos(self, x, y):
        """Return screen-space (x, y) for drawing, given world-space (x, y)."""
        return x - self.offset_x, y - self.offset_y