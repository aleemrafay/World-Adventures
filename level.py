"""
level.py
Parses a level's character grid into actual game objects: solid tiles,
coins, power-ups, enemies, player spawn, and the finish flag. Handles
per-frame updates (collisions, coin pickup, enemy stomps, death by
falling, reaching the flag) and drawing everything through the camera.
"""

import pygame

from settings import (
    TILE_SIZE, COLOR_GROUND, COLOR_GROUND_TOP, COLOR_BRICK, COLOR_COIN,
    COLOR_POWERUP, COLOR_FLAG, COIN_SCORE, ENEMY_STOMP_SCORE,
    LEVEL_COMPLETE_BONUS, SCREEN_HEIGHT, STATE_LEVEL_COMPLETE
)
from player import Player
from enemy import Enemy, check_stomp_or_hit
from camera import Camera


class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + TILE_SIZE // 4, y + TILE_SIZE // 4,
                                 TILE_SIZE // 2, TILE_SIZE // 2)
        self.collected = False
        self.bob_timer = 0.0

    def update(self, dt):
        self.bob_timer += dt * 4

    def draw(self, screen, camera):
        if self.collected:
            return
        import math
        offset = int(math.sin(self.bob_timer) * 4)
        r = camera.apply(self.rect)
        r.y += offset
        pygame.draw.ellipse(screen, COLOR_COIN, r)
        pygame.draw.ellipse(screen, (200, 160, 0), r, 2)


class PowerUp:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 4, y + 4, TILE_SIZE - 8, TILE_SIZE - 8)
        self.collected = False

    def draw(self, screen, camera):
        if self.collected:
            return
        r = camera.apply(self.rect)
        pygame.draw.rect(screen, COLOR_POWERUP, r, border_radius=6)
        pygame.draw.rect(screen, (150, 60, 0), r, 3, border_radius=6)


class Flag:
    def __init__(self, x, y_top, y_bottom):
        self.rect = pygame.Rect(x, y_top, TILE_SIZE // 3, y_bottom - y_top)

    def draw(self, screen, camera):
        r = camera.apply(self.rect)
        pygame.draw.rect(screen, (120, 120, 120), (r.x + r.width // 2 - 2, r.y, 4, r.height))
        pygame.draw.polygon(screen, COLOR_FLAG, [
            (r.x + r.width // 2 + 2, r.y),
            (r.x + r.width // 2 + 2 + 24, r.y + 10),
            (r.x + r.width // 2 + 2, r.y + 20),
        ])


class Level:
    def __init__(self, level_data, game):
        self.game = game
        self.name = level_data["name"]
        self.grid = level_data["grid"]

        self.solid_tiles = []       # list of pygame.Rect for collision
        self.brick_tiles = []       # separate for drawing color distinction
        self.coins = []
        self.powerups = []
        self.enemies = []
        self.flag = None
        self.player = None

        self.completed = False
        self.transition_timer = 0.0

        self._parse_grid()

        level_width_px = len(self.grid[0]) * TILE_SIZE
        level_height_px = len(self.grid) * TILE_SIZE
        self.width_px = level_width_px
        self.height_px = level_height_px
        self.camera = Camera(level_width_px, level_height_px)

    # ------------------------------------------------------------------
    def _parse_grid(self):
        rows = self.grid
        for row_index, row in enumerate(rows):
            for col_index, char in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if char == "G":
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.solid_tiles.append(rect)

                elif char == "B":
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.solid_tiles.append(rect)
                    self.brick_tiles.append(rect)

                elif char == "C":
                    self.coins.append(Coin(x, y))

                elif char == "P":
                    self.powerups.append(PowerUp(x, y))

                elif char == "S":
                    self.player = Player(x, y - TILE_SIZE)  # spawn just above ground

                elif char == "F":
                    # Flag spans from this row up to the ground line
                    ground_y = self._find_ground_y(col_index)
                    self.flag = Flag(x, y - TILE_SIZE * 3, ground_y)

                elif char == "E":
                    left_bound, right_bound = self._find_platform_bounds(row_index, col_index)
                    enemy = Enemy(x, y - TILE_SIZE, left_bound, right_bound)
                    self.enemies.append(enemy)

        if self.player is None:
            # Fallback spawn if no 'S' found
            self.player = Player(TILE_SIZE, SCREEN_HEIGHT - TILE_SIZE * 3)

    def _find_ground_y(self, col_index):
        """Find the y pixel of the topmost solid tile in this column."""
        for row_index, row in enumerate(self.grid):
            if col_index < len(row) and row[col_index] in ("G", "B"):
                return row_index * TILE_SIZE
        return len(self.grid) * TILE_SIZE

    def _find_platform_bounds(self, row_index, col_index):
        """
        Given an enemy's row/col, find the contiguous solid platform
        directly beneath it (one row down) so the enemy patrols without
        walking off the edge.
        """
        ground_row = row_index + 1
        if ground_row >= len(self.grid):
            ground_row = len(self.grid) - 1
        row = self.grid[ground_row]

        left = col_index
        while left > 0 and left - 1 < len(row) and row[left - 1] in ("G", "B"):
            left -= 1
        right = col_index
        while right + 1 < len(row) and row[right + 1] in ("G", "B"):
            right += 1

        return left * TILE_SIZE, (right + 1) * TILE_SIZE

    # ------------------------------------------------------------------
    def update(self, dt):
        if self.completed:
            self.transition_timer += dt
            if self.transition_timer > 1.0:
                self.game.next_level()
            return

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self.solid_tiles)

        # Fell into a pit -> death
        if self.player.rect.top > self.height_px:
            self.player.alive = False

        if not self.player.alive:
            self.game.player_died()
            return

        self.camera.update(self.player.rect)

        # Coins
        for coin in self.coins:
            coin.update(dt)
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.game.total_score += COIN_SCORE

        # Power-ups
        for pu in self.powerups:
            if not pu.collected and self.player.rect.colliderect(pu.rect):
                pu.collected = True
                self.player.grow()

        # Enemies
        for enemy in self.enemies:
            enemy.update(dt, self.solid_tiles)
            result = check_stomp_or_hit(self.player, enemy)
            if result == "stomp":
                enemy.squash()
                self.game.total_score += ENEMY_STOMP_SCORE
                self.player.vel_y = -300  # small bounce after stomping
            elif result == "hit":
                self.player.take_damage()

        self.enemies = [e for e in self.enemies if e.alive]

        # Flag / level complete
        if self.flag and self.player.rect.colliderect(self.flag.rect):
            self.completed = True
            self.transition_timer = 0.0
            self.game.total_score += LEVEL_COMPLETE_BONUS

    # ------------------------------------------------------------------
    def draw(self, screen):
        # Ground tiles
        for rect in self.solid_tiles:
            is_brick = rect in self.brick_tiles
            screen_rect = self.camera.apply(rect)
            if is_brick:
                pygame.draw.rect(screen, COLOR_BRICK, screen_rect)
                pygame.draw.rect(screen, (100, 50, 20), screen_rect, 2)
            else:
                pygame.draw.rect(screen, COLOR_GROUND, screen_rect)
                top_strip = pygame.Rect(screen_rect.x, screen_rect.y, screen_rect.width, 8)
                pygame.draw.rect(screen, COLOR_GROUND_TOP, top_strip)

        for coin in self.coins:
            coin.draw(screen, self.camera)

        for pu in self.powerups:
            pu.draw(screen, self.camera)

        if self.flag:
            self.flag.draw(screen, self.camera)

        for enemy in self.enemies:
            enemy.draw(screen, self.camera)

        self.player.draw(screen, self.camera)