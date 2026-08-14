# World-Adventures. 🎮

A Mario-style 2D platformer built from scratch in Python using **Pygame**, featuring custom physics, side-scrolling camera, enemy AI, power-ups, and multi-level progression.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green)
![Status](https://img.shields.io/badge/status-in--progress-yellow)

## 🕹️ Overview

This project recreates the core mechanics of classic Mario-style platformers — running, jumping, stomping enemies, collecting coins, and growing with power-ups — using a clean, modular Object-Oriented architecture in Python.

## ✨ Features

- **Smooth physics-based movement** — gravity, jumping, friction, and axis-by-axis collision resolution
- **Side-scrolling camera** that follows the player and clamps to level bounds
- **Enemy AI** — patrolling enemies with stomp-to-defeat and side-collision damage mechanics
- **Power-up system** — collect items to grow and take an extra hit before dying
- **Sprite-based animation** — idle, walk, jump, fall, duck, and hurt states
- **Coin collection & scoring system**
- **Multi-level progression** with flag-based level completion
- **Lives system** with game-over and win states
- **Grid-based level design** — levels are defined as readable text grids for easy editing

## 🎮 Controls

| Key                  | Action        |
|-----------------------|---------------|
| `LEFT` / `A`           | Move left     |
| `RIGHT` / `D`          | Move right    |
| `SPACE` / `UP` / `W`   | Jump          |
| `DOWN` / `S`           | Duck          |
| `R`                    | Restart level |
| `ESC`                  | Quit game     |

## 📁 Project Structure

```
mario_game/
├── main.py            # Entry point, game loop, and state management
├── settings.py         # Global constants (physics, colors, screen config)
├── player.py            # Player class — movement, animation, power-ups
├── enemy.py               # Enemy class — patrol AI, stomp/hit detection
├── camera.py                # Side-scrolling camera logic
├── level.py                   # Level parsing, collisions, coins, flags
├── levels_data.py               # Level layouts as text-based grids
├── ui.py                          # HUD and game-over/win screens
└── assets/
    ├── player/                        # Player sprite frames
    ├── enemy/                          # Enemy sprite frames
    └── items/                           # Coin / power-up sprites
```

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Pygame

### Installation

```bash
git clone https://github.com/aleemrafay/World-Adventures.git
cd World-Adventures
pip install pygame
```

### Run the game

```bash
python main.py
```

## 🏗️ Architecture Notes

The game follows a modular OOP design:

- **`Player`** handles its own physics, input, animation state, and power-up/damage logic
- **`Enemy`** manages patrol movement, wall/platform detection, and squash animation
- **`Level`** parses a text grid into game objects (tiles, coins, power-ups, enemies, flag) and owns per-frame collision/update logic
- **`Camera`** decouples world coordinates from screen coordinates for scrolling
- **`Game`** (in `main.py`) manages overall state — score, lives, level progression, and game-over/win flow

Levels are defined as simple character grids in `levels_data.py`, making it easy to design new levels without touching game logic:

```
G = ground   B = brick   C = coin   P = power-up
E = enemy    S = spawn   F = flag   . = empty space
```

## 🎨 Assets

Character and enemy sprites from [Kenney.nl](https://kenney.nl) (CC0 licensed, free for commercial and personal use).

## 📌 Roadmap / Planned Improvements

- [ ] Additional enemy types
- [ ] Sound effects (jump, coin, stomp)
- [ ] More levels
- [ ] Parallax scrolling backgrounds
- [ ] Checkpoint system

## 👤 Author

**Rafay** ([@aleemrafay](https://github.com/aleemrafay))
BS Artificial Intelligence, University of Central Punjab

## 📄 License

This project is for educational purposes. Sprite assets are CC0 licensed via Kenney.nl.