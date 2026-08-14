"""
ui.py
Draws the heads-up display (score, lives, level indicator) during
gameplay, and full-screen messages for game over / win states.
"""

import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_TEXT_SHADOW, COLOR_BLACK


def _draw_text_with_shadow(screen, font, text, x, y, color=COLOR_WHITE):
    shadow = font.render(text, True, COLOR_TEXT_SHADOW)
    screen.blit(shadow, (x + 2, y + 2))
    main_surf = font.render(text, True, color)
    screen.blit(main_surf, (x, y))


def draw_hud(screen, font, score, lives, level_num, total_levels):
    """Top-left: score, lives, and current level indicator."""
    _draw_text_with_shadow(screen, font, f"SCORE: {score}", 20, 16)
    _draw_text_with_shadow(screen, font, f"LIVES: {lives}", 20, 50)

    level_text = f"LEVEL {level_num}/{total_levels}"
    text_surf = font.render(level_text, True, COLOR_WHITE)
    x = SCREEN_WIDTH - text_surf.get_width() - 20
    _draw_text_with_shadow(screen, font, level_text, x, 16)


def draw_message_screen(screen, font, title, subtitle, hint):
    """Full-screen overlay for GAME OVER / WIN states."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(COLOR_BLACK)
    screen.blit(overlay, (0, 0))

    big_font = pygame.font.SysFont("consolas", 56, bold=True)
    title_surf = big_font.render(title, True, COLOR_WHITE)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
    screen.blit(title_surf, title_rect)

    sub_surf = font.render(subtitle, True, COLOR_WHITE)
    sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(sub_surf, sub_rect)

    hint_surf = font.render(hint, True, (200, 200, 200))
    hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(hint_surf, hint_rect)