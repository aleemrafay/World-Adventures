"""
Mario-style Platformer
Entry point - run this file to play.

    python main.py

Controls:
    LEFT/RIGHT  - move
    SPACE / UP  - jump
    R           - restart level after death
    ESC         - quit
"""

import pygame
import sys

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    STATE_PLAYING, STATE_LEVEL_COMPLETE, STATE_GAME_OVER, STATE_WIN
)
from level import Level
from levels_data import LEVELS
from ui import draw_hud, draw_message_screen


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.total_score = 0
        self.lives = 3
        self.current_level_index = 0

        self.state = STATE_PLAYING
        self.level = None
        self.load_level(self.current_level_index)

        self.font = pygame.font.SysFont("consolas", 28, bold=True)

    def load_level(self, index):
        level_data = LEVELS[index]
        self.level = Level(level_data, self)
        self.state = STATE_PLAYING

    def next_level(self):
        self.current_level_index += 1
        if self.current_level_index >= len(LEVELS):
            self.state = STATE_WIN
        else:
            self.load_level(self.current_level_index)

    def restart_level(self):
        self.load_level(self.current_level_index)

    def player_died(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = STATE_GAME_OVER
        else:
            self.load_level(self.current_level_index)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if self.state in (STATE_GAME_OVER, STATE_WIN) and event.key == pygame.K_r:
                    self.total_score = 0
                    self.lives = 3
                    self.current_level_index = 0
                    self.load_level(0)

                if self.state == STATE_PLAYING and event.key == pygame.K_r:
                    self.restart_level()

    def update(self, dt):
        if self.state == STATE_PLAYING:
            self.level.update(dt)

    def draw(self):
        self.screen.fill((92, 148, 252))  # classic sky blue

        if self.state == STATE_PLAYING:
            self.level.draw(self.screen)
            draw_hud(self.screen, self.font, self.total_score, self.lives,
                     self.current_level_index + 1, len(LEVELS))

        elif self.state == STATE_GAME_OVER:
            draw_message_screen(self.screen, self.font, "GAME OVER",
                                 f"Final Score: {self.total_score}",
                                 "Press R to restart")

        elif self.state == STATE_WIN:
            draw_message_screen(self.screen, self.font, "YOU WIN!",
                                 f"Final Score: {self.total_score}",
                                 "Press R to play again")

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()