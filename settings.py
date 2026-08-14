"""
settings.py
All game-wide constants live here — screen config, physics, colors, and state names.
"""

# ---------- Display ----------
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
TITLE = "Super Rafay Bros."

TILE_SIZE = 40

# ---------- Physics ----------
GRAVITY = 1400          # px/s^2
PLAYER_SPEED = 260       # px/s horizontal
PLAYER_JUMP_STRENGTH = -560  # px/s (negative = up)
MAX_FALL_SPEED = 900
FRICTION = 0.85          # ground deceleration multiplier

# ---------- Player ----------
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_INVINCIBLE_TIME = 1.2   # seconds after taking damage

# ---------- Enemy ----------
ENEMY_SPEED = 80
ENEMY_WIDTH = 34
ENEMY_HEIGHT = 34

# ---------- Colors ----------
COLOR_GROUND = (94, 51, 30)
COLOR_GROUND_TOP = (60, 179, 75)
COLOR_BRICK = (170, 90, 50)
COLOR_COIN = (255, 215, 0)
COLOR_PLAYER = (220, 30, 30)
COLOR_PLAYER_BIG = (200, 20, 90)
COLOR_ENEMY = (110, 60, 20)
COLOR_POWERUP = (255, 120, 20)
COLOR_FLAG = (240, 240, 240)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_TEXT_SHADOW = (30, 30, 30)

# ---------- Game States ----------
STATE_PLAYING = "playing"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_OVER = "game_over"
STATE_WIN = "win"

# ---------- Scoring ----------
COIN_SCORE = 100
ENEMY_STOMP_SCORE = 200
LEVEL_COMPLETE_BONUS = 500