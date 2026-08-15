"""
background.py
Layered parallax background using real PNG assets: sky, hills, clouds,
and trees. Hills and trees are color-tinted since the source PNGs are
outline/silhouette shapes with transparent fill. Each layer scrolls at
a different speed relative to the camera to create a sense of depth.
"""

import os
import pygame
import random

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets", "background")


def load_image(filename):
    path = os.path.join(ASSETS_PATH, filename)
    return pygame.image.load(path).convert_alpha()


def tint_image(image, color):
    """
    Tints a (possibly outline-only / semi-transparent) image with a solid
    color while preserving its alpha shape. Uses BLEND_RGBA_MULT so any
    transparent pixels stay transparent, but visible pixels become 'color'.
    """
    tinted = image.copy()
    overlay = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    overlay.fill(color)
    tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


class Background:
    def __init__(self, level_width_px, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.level_width_px = level_width_px

        random.seed(42)

        # ---------- Sky (static base layer, stretched to fill screen) ----------
        sky_raw = load_image("sky.png")
        self.sky = pygame.transform.smoothscale(sky_raw, (screen_width, screen_height))

        # ---------- Far hills (slow parallax, darker/muted green) ----------
        far_raw = load_image("hills1.png")
        far_raw = tint_image(far_raw, (120, 180, 130, 255))
        far_h = int(screen_height * 0.45)
        scale = far_h / far_raw.get_height()
        far_w = int(far_raw.get_width() * scale)
        self.far_hills_img = pygame.transform.smoothscale(far_raw, (far_w, far_h))
        self.far_parallax = 0.15

        # ---------- Near hills (medium parallax, richer green) ----------
        near_raw = load_image("hills1.png")
        near_raw = tint_image(near_raw, (70, 160, 90, 255))
        near_h = int(screen_height * 0.28)
        scale = near_h / near_raw.get_height()
        near_w = int(near_raw.get_width() * scale)
        self.near_hills_img = pygame.transform.smoothscale(near_raw, (near_w, near_h))
        self.near_parallax = 0.35

        # ---------- Clouds (scattered, slowest parallax, floats high) ----------
        cloud_files = ["cloud1.png", "cloud2.png", "cloud3.png"]
        cloud_images_raw = [load_image(f) for f in cloud_files]
        self.clouds = []
        num_clouds = max(6, level_width_px // 350)
        for _ in range(num_clouds):
            img_raw = random.choice(cloud_images_raw)
            target_w = random.randint(60, 110)
            scale = target_w / img_raw.get_width()
            img = pygame.transform.smoothscale(
                img_raw, (target_w, int(img_raw.get_height() * scale))
            )
            x = random.randint(0, level_width_px)
            y = random.randint(20, 140)
            self.clouds.append({"img": img, "x": x, "y": y})
        self.cloud_parallax = 0.1

        # ---------- Trees (closest decorative layer, fastest parallax, brown+green tint) ----------
        tree_files = ["tree01.png", "tree02.png", "tree03.png"]
        tree_images_raw = [load_image(f) for f in tree_files]
        self.trees = []
        num_trees = max(8, level_width_px // 220)
        for _ in range(num_trees):
            img_raw = random.choice(tree_images_raw)
            img_raw = tint_image(img_raw, (50, 130, 70, 255))
            target_h = random.randint(70, 110)
            scale = target_h / img_raw.get_height()
            img = pygame.transform.smoothscale(
                img_raw, (int(img_raw.get_width() * scale), target_h)
            )
            x = random.randint(0, level_width_px)
            self.trees.append({"img": img, "x": x})
        self.tree_parallax = 0.6

    # ------------------------------------------------------------------
    def _draw_tiled_layer(self, screen, image, offset_x, y):
        img_w = image.get_width()
        start_x = -(offset_x % img_w) - img_w
        x = start_x
        while x < self.screen_width + img_w:
            screen.blit(image, (x, y))
            x += img_w

    def draw(self, screen, camera_offset_x):
        screen.blit(self.sky, (0, 0))

        far_offset = camera_offset_x * self.far_parallax
        far_y = self.screen_height - self.far_hills_img.get_height() - 40
        self._draw_tiled_layer(screen, self.far_hills_img, far_offset, far_y)

        near_offset = camera_offset_x * self.near_parallax
        near_y = self.screen_height - self.near_hills_img.get_height() - 20
        self._draw_tiled_layer(screen, self.near_hills_img, near_offset, near_y)

        cloud_offset = camera_offset_x * self.cloud_parallax
        for cloud in self.clouds:
            screen_x = cloud["x"] - cloud_offset
            if -150 < screen_x < self.screen_width + 150:
                screen.blit(cloud["img"], (screen_x, cloud["y"]))

        tree_offset = camera_offset_x * self.tree_parallax
        ground_y = self.screen_height - 40
        for tree in self.trees:
            screen_x = tree["x"] - tree_offset
            if -150 < screen_x < self.screen_width + 150:
                draw_y = ground_y - tree["img"].get_height()
                screen.blit(tree["img"], (screen_x, draw_y))