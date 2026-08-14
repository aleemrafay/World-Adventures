"""
player.py
Player class: handles movement physics, jumping, sprite animation,
power-up state (small/big), collision with the level, and taking damage.
"""

import os
import pygame

from settings import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_JUMP_STRENGTH,
    GRAVITY, MAX_FALL_SPEED, FRICTION, TILE_SIZE, PLAYER_INVINCIBLE_TIME
)

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets", "player")


def load_sprite(filename, target_height):
    """Load a PNG and scale it to target_height, preserving aspect ratio."""
    path = os.path.join(ASSETS_PATH, filename)
    image = pygame.image.load(path).convert_alpha()
    w, h = image.get_size()
    scale = target_height / h
    new_size = (int(w * scale), int(h * scale))
    return pygame.transform.smoothscale(image, new_size)


class Player:
    # Animation timing
    WALK_FRAME_DURATION = 0.12  # seconds per walk frame

    def __init__(self, x, y):
        # ---------- State ----------
        self.big = False               # power-up state
        self.facing_right = True
        self.on_ground = False
        self.alive = True
        self.invincible_timer = 0.0    # after taking damage
        self.hurt_flash_timer = 0.0

        # ---------- Physics ----------
        self.vel_x = 0.0
        self.vel_y = 0.0

        # ---------- Position / hitbox (world coordinates) ----------
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # ---------- Sprites ----------
        self._load_all_sprites()
        self.current_frame_name = "idle"
        self.walk_frame_index = 0
        self.walk_timer = 0.0

    # ------------------------------------------------------------------
    # Sprite loading
    # ------------------------------------------------------------------
    def _load_all_sprites(self):
        """
        Loads both small and big versions of each pose by scaling to the
        appropriate pixel height. Stored in two dicts: self.sprites_small
        and self.sprites_big.
        """
        small_h = PLAYER_HEIGHT
        big_h = int(PLAYER_HEIGHT * 1.4)

        pose_files = {
            "idle": "player_idle.png",
            "walk1": "player_walk1.png",
            "walk2": "player_walk2.png",
            "jump": "player_jump.png",
            "fall": "player_fall.png",
            "duck": "player_duck.png",
            "hurt": "player_hurt.png",
        }

        self.sprites_small = {}
        self.sprites_big = {}
        for name, filename in pose_files.items():
            self.sprites_small[name] = load_sprite(filename, small_h)
            self.sprites_big[name] = load_sprite(filename, big_h)

    def _current_sprite_set(self):
        return self.sprites_big if self.big else self.sprites_small

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------
    def handle_input(self, keys):
        if not self.alive:
            return

        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
            moving = True
        else:
            self.vel_x *= FRICTION
            if abs(self.vel_x) < 5:
                self.vel_x = 0

        self.ducking = (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.on_ground

        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        if jump_pressed and self.on_ground and not self.ducking:
            self.vel_y = PLAYER_JUMP_STRENGTH
            self.on_ground = False

        return moving

    # ------------------------------------------------------------------
    # Physics + collision
    # ------------------------------------------------------------------
    def apply_gravity(self, dt):
        self.vel_y += GRAVITY * dt
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

    def move_and_collide(self, dt, solid_tiles):
        """
        solid_tiles: list of pygame.Rect representing solid level geometry.
        Moves the player and resolves collisions axis-by-axis (standard
        platformer approach: move X, resolve X; move Y, resolve Y).
        """
        # --- Horizontal ---
        self.rect.x += round(self.vel_x * dt)
        for tile in solid_tiles:
            if self.rect.colliderect(tile):
                if self.vel_x > 0:
                    self.rect.right = tile.left
                elif self.vel_x < 0:
                    self.rect.left = tile.right
                self.vel_x = 0

        # --- Vertical ---
        self.rect.y += round(self.vel_y * dt)
        self.on_ground = False
        for tile in solid_tiles:
            if self.rect.colliderect(tile):
                if self.vel_y > 0:
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = tile.bottom
                    self.vel_y = 0

    # ------------------------------------------------------------------
    # Power-up / damage
    # ------------------------------------------------------------------
    def grow(self):
        """Called when player collects a power-up."""
        if not self.big:
            old_bottom = self.rect.bottom
            self.big = True
            self.height = int(PLAYER_HEIGHT * 1.4)
            self.rect.height = self.height
            self.rect.bottom = old_bottom  # keep feet planted

    def take_damage(self):
        if self.invincible_timer > 0:
            return  # can't be hurt again mid-invincibility

        if self.big:
            # Shrink back to small instead of dying
            old_bottom = self.rect.bottom
            self.big = False
            self.height = PLAYER_HEIGHT
            self.rect.height = self.height
            self.rect.bottom = old_bottom
            self.invincible_timer = PLAYER_INVINCIBLE_TIME
        else:
            self.alive = False

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------
    def update_animation(self, dt, moving):
        if not self.on_ground:
            self.current_frame_name = "fall" if self.vel_y > 0 else "jump"
        elif getattr(self, "ducking", False):
            self.current_frame_name = "duck"
        elif moving and abs(self.vel_x) > 10:
            self.walk_timer += dt
            if self.walk_timer >= self.WALK_FRAME_DURATION:
                self.walk_timer = 0.0
                self.walk_frame_index = 1 - self.walk_frame_index
            self.current_frame_name = "walk1" if self.walk_frame_index == 0 else "walk2"
        else:
            self.current_frame_name = "idle"

    # ------------------------------------------------------------------
    # Update / Draw
    # ------------------------------------------------------------------
    def update(self, dt, keys, solid_tiles):
        if not self.alive:
            return

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        moving = self.handle_input(keys)
        self.apply_gravity(dt)
        self.move_and_collide(dt, solid_tiles)
        self.update_animation(dt, moving)

    def draw(self, screen, camera):
        sprite_set = self._current_sprite_set()

        if self.invincible_timer > 0:
            # Flicker effect while invincible
            self.hurt_flash_timer += 1
            if int(self.hurt_flash_timer) % 6 < 3:
                sprite = sprite_set.get("hurt", sprite_set["idle"])
            else:
                return  # skip drawing this frame = flicker
        else:
            sprite = sprite_set[self.current_frame_name]

        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)

        # Align sprite bottom-center to hitbox bottom-center
        draw_x = self.rect.centerx - sprite.get_width() // 2
        draw_y = self.rect.bottom - sprite.get_height()
        screen_x, screen_y = camera.apply_pos(draw_x, draw_y)
        screen.blit(sprite, (screen_x, screen_y))