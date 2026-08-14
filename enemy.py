"""
enemy.py
Basic patrolling enemy (Goomba-style). Walks back and forth within its
level bounds, turns around at edges/walls, and can be stomped from above.
"""

import os
import pygame

from settings import ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_SPEED, GRAVITY, MAX_FALL_SPEED

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets", "enemy")


class Enemy:
    def __init__(self, x, y, patrol_left, patrol_right):
        """
        x, y: starting world position (top-left)
        patrol_left, patrol_right: world x-coordinates the enemy won't cross
        """
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.patrol_left = patrol_left
        self.patrol_right = patrol_right

        self.vel_x = -ENEMY_SPEED
        self.vel_y = 0.0
        self.alive = True
        self.squashed = False
        self.squash_timer = 0.0  # brief pause before removal, for visual feedback

        self.facing_right = False
        self._load_sprites()
        self.walk_timer = 0.0
        self.walk_frame_index = 0

    # ------------------------------------------------------------------
    def _load_sprites(self):
        """
        Tries to load enemy sprites from assets/enemy/. If not found,
        falls back to a simple colored rectangle drawn in draw().
        """
        self.sprites = None
        try:
            walk1 = pygame.image.load(os.path.join(ASSETS_PATH, "enemy_walk1.png")).convert_alpha()
            walk2 = pygame.image.load(os.path.join(ASSETS_PATH, "enemy_walk2.png")).convert_alpha()
            squashed = pygame.image.load(os.path.join(ASSETS_PATH, "enemy_squashed.png")).convert_alpha()

            def scale(img, h):
                w, ih = img.get_size()
                s = h / ih
                return pygame.transform.smoothscale(img, (int(w * s), h))

            self.sprites = {
                "walk1": scale(walk1, self.height),
                "walk2": scale(walk2, self.height),
                "squashed": scale(squashed, self.height // 2),
            }
        except (pygame.error, FileNotFoundError):
            self.sprites = None  # will use fallback rectangle drawing

    # ------------------------------------------------------------------
    def update(self, dt, solid_tiles):
        if self.squashed:
            self.squash_timer += dt
            if self.squash_timer > 0.4:
                self.alive = False
            return

        # Gravity
        self.vel_y += GRAVITY * dt
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Horizontal movement + patrol bounds
        self.rect.x += round(self.vel_x * dt)
        if self.rect.left <= self.patrol_left:
            self.rect.left = self.patrol_left
            self.vel_x = abs(self.vel_x)
        elif self.rect.right >= self.patrol_right:
            self.rect.right = self.patrol_right
            self.vel_x = -abs(self.vel_x)

        self.facing_right = self.vel_x > 0

        # Horizontal collision with solid tiles (turn around on wall hit)
        for tile in solid_tiles:
            if self.rect.colliderect(tile):
                if self.vel_x > 0:
                    self.rect.right = tile.left
                    self.vel_x = -abs(self.vel_x)
                elif self.vel_x < 0:
                    self.rect.left = tile.right
                    self.vel_x = abs(self.vel_x)

        # Vertical collision
        self.rect.y += round(self.vel_y * dt)
        for tile in solid_tiles:
            if self.rect.colliderect(tile):
                if self.vel_y > 0:
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = tile.bottom
                    self.vel_y = 0

        # Animation timing
        self.walk_timer += dt
        if self.walk_timer >= 0.2:
            self.walk_timer = 0.0
            self.walk_frame_index = 1 - self.walk_frame_index

    def squash(self):
        """Called when the player stomps this enemy from above."""
        self.squashed = True
        self.vel_x = 0
        self.squash_timer = 0.0

    # ------------------------------------------------------------------
    def draw(self, screen, camera):
        screen_rect = camera.apply(self.rect)

        if self.sprites:
            if self.squashed:
                sprite = self.sprites["squashed"]
                draw_y = self.rect.bottom - sprite.get_height()
            else:
                sprite = self.sprites["walk1"] if self.walk_frame_index == 0 else self.sprites["walk2"]
                if self.facing_right:
                    sprite = pygame.transform.flip(sprite, True, False)
                draw_y = self.rect.bottom - sprite.get_height()

            draw_x = self.rect.centerx - sprite.get_width() // 2
            sx, sy = camera.apply_pos(draw_x, draw_y)
            screen.blit(sprite, (sx, sy))
        else:
            # Fallback: simple colored rectangle if no sprites found
            from settings import COLOR_ENEMY
            color = COLOR_ENEMY if not self.squashed else (80, 40, 15)
            rect = screen_rect
            if self.squashed:
                rect = pygame.Rect(rect.x, rect.bottom - rect.height // 2, rect.width, rect.height // 2)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)


def check_stomp_or_hit(player, enemy):
    """
    Checks collision between player and enemy, returns one of:
    'stomp', 'hit', or None.

    'stomp'  -> player was falling and hit enemy from above -> enemy squashed
    'hit'    -> player touched enemy from the side -> player takes damage
    """
    if not enemy.alive or enemy.squashed:
        return None
    if not player.rect.colliderect(enemy.rect):
        return None

    # Stomp condition: player's bottom was above enemy's top-half AND player is falling
    player_prev_bottom = player.rect.bottom - player.vel_y * (1 / 60)  # rough estimate
    falling = player.vel_y > 0
    landed_on_top = player.rect.bottom <= enemy.rect.top + (enemy.rect.height * 0.5)

    if falling and landed_on_top:
        return "stomp"
    return "hit"