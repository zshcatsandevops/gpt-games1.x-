#!/usr/bin/env python3
"""
Super Mario 1-1 — Full Scrolling Demo (Pygame)
----------------------------------------------
A minimal but complete side-scroller inspired by SMB 1-1.
Features: camera scrolling, coins, Goombas, flagpole, and goal castle.

(C) 2025 Flames Co. / Samsoft Interactive
"""

import sys
import random
import pygame as pg

# ------------------------------------------------------------------
# 1.  Constants
# ------------------------------------------------------------------
SCREEN_W, SCREEN_H = 800, 480
FPS = 60

# Colours
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
GREEN   = (34, 139, 34)
BLUE    = (135, 206, 235)
BROWN   = (139, 69, 19)
YELLOW  = (255, 215, 0)
RED     = (255, 0, 0)
GRAY    = (100, 100, 100)
FLAGGREEN = (0, 200, 0)

# Geometry
TILE_W, TILE_H = 50, 20
GROUND_Y = SCREEN_H - 40
WORLD_W  = 5500

# Mario
MARIO_W, MARIO_H = 32, 48
MARIO_SPEED = 200
JUMP_FORCE  = -420
GRAVITY     = 900


# ------------------------------------------------------------------
# 2.  Helpers
# ------------------------------------------------------------------
def draw_sky(surface): surface.fill(BLUE)

def draw_ground(surface, camera_x):
    for i in range(0, WORLD_W, TILE_W):
        pg.draw.rect(surface, GREEN, (i - camera_x, GROUND_Y, TILE_W, TILE_H))

def draw_block(surface, x, y, camera_x):
    rect = pg.Rect(x - camera_x, y, TILE_W, TILE_H)
    pg.draw.rect(surface, BROWN, rect)
    pg.draw.rect(surface, (160, 82, 45), rect, 2)

def draw_coin(surface, x, y, camera_x):
    r = 8
    pg.draw.circle(surface, YELLOW, (x - camera_x, y), r)
    pg.draw.circle(surface, (255, 255, 0), (x - camera_x - 3, y - 3), r // 2)

def draw_flag(surface, x, camera_x):
    base_x = x - camera_x
    pg.draw.rect(surface, GRAY, (base_x, GROUND_Y - 160, 6, 160))
    pg.draw.polygon(surface, FLAGGREEN, [(base_x + 6, GROUND_Y - 160),
                                         (base_x + 60, GROUND_Y - 140),
                                         (base_x + 6, GROUND_Y - 120)])

def draw_castle(surface, x, camera_x):
    bx = x - camera_x
    pg.draw.rect(surface, BROWN, (bx, GROUND_Y - 100, 120, 100))
    pg.draw.rect(surface, BLACK, (bx + 40, GROUND_Y - 60, 40, 60))  # door


# ------------------------------------------------------------------
# 3.  Classes
# ------------------------------------------------------------------
class Goomba:
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y - 24, 32, 24)
        self.vel_x = random.choice([-60, 60])
        self.dead = False

    def update(self, dt, blocks):
        if self.dead: return
        self.rect.x += self.vel_x * dt
        # turn around on edge or block hit
        on_ground = False
        for bx, by in blocks:
            b = pg.Rect(bx, by, TILE_W, TILE_H)
            if self.rect.colliderect(b):
                if self.vel_x > 0:
                    self.rect.right = b.left
                else:
                    self.rect.left = b.right
                self.vel_x *= -1
            # standing on top check
            under = pg.Rect(bx, by - 2, TILE_W, 2)
            if self.rect.colliderect(under): on_ground = True
        # gravity
        if not on_ground:
            self.rect.y += int(GRAVITY * dt)

    def draw(self, surf, cam_x):
        if self.dead: return
        pg.draw.rect(surf, (139, 69, 19), (self.rect.x - cam_x, self.rect.y, self.rect.w, self.rect.h))


# ------------------------------------------------------------------
# 4.  Level
# ------------------------------------------------------------------
def build_level():
    blocks, coins, goombas = [], [], []

    # Ground
    for i in range(0, WORLD_W, TILE_W):
        blocks.append((i, GROUND_Y))

    # Platforms
    for i in range(400, 1400, TILE_W):
        blocks.append((i, GROUND_Y - 80))
    for i in range(2000, 2300, TILE_W):
        blocks.append((i, GROUND_Y - 100))
    for i in range(2800, 3000, TILE_W):
        blocks.append((i, GROUND_Y - 60))

    # Coins
    for i in range(450, 1350, TILE_W):
        coins.append([i + TILE_W // 2, GROUND_Y - 100, True])
    for i in range(2050, 2250, 100):
        coins.append([i + 25, GROUND_Y - 120, True])

    # Goombas
    goombas.append(Goomba(800, GROUND_Y - 24))
    goombas.append(Goomba(1600, GROUND_Y - 24))
    goombas.append(Goomba(2500, GROUND_Y - 24))
    goombas.append(Goomba(3400, GROUND_Y - 24))

    return blocks, coins, goombas


# ------------------------------------------------------------------
# 5.  Camera
# ------------------------------------------------------------------
class Camera:
    def __init__(self):
        self.x = 0
    def update(self, target_rect):
        self.x = max(0, min(target_rect.centerx - SCREEN_W // 2, WORLD_W - SCREEN_W))


# ------------------------------------------------------------------
# 6.  Main
# ------------------------------------------------------------------
def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_W, SCREEN_H))
    pg.display.set_caption("Super Mario 1-1 — Full Demo")
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 24)

    blocks, coins, goombas = build_level()
    camera = Camera()

    mario_x, mario_y = 50, GROUND_Y - MARIO_H
    vel_y = 0
    on_ground = False
    score = 0
    goal_x = WORLD_W - 250

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Events
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit(); sys.exit()

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:  mario_x -= MARIO_SPEED * dt
        if keys[pg.K_RIGHT]: mario_x += MARIO_SPEED * dt
        if keys[pg.K_SPACE] and on_ground:
            vel_y = JUMP_FORCE; on_ground = False

        # Gravity
        vel_y += GRAVITY * dt
        mario_y += vel_y * dt

        # Collisions
        mario_rect = pg.Rect(mario_x, mario_y, MARIO_W, MARIO_H)
        on_ground = False
        for bx, by in blocks:
            b = pg.Rect(bx, by, TILE_W, TILE_H)
            if mario_rect.colliderect(b) and vel_y > 0:
                mario_y = b.top - MARIO_H
                vel_y = 0; on_ground = True

        # Coins
        for c in coins:
            if c[2] and pg.Rect(c[0]-8, c[1]-8, 16, 16).colliderect(mario_rect):
                c[2] = False; score += 100

        # Goombas
        for g in goombas:
            g.update(dt, blocks)
            if not g.dead and mario_rect.colliderect(g.rect):
                if vel_y > 0:
                    g.dead = True
                    vel_y = JUMP_FORCE / 2
                    score += 200
                else:
                    running = False  # hit -> game over

        # Death or win
        if mario_y > SCREEN_H: running = False
        if mario_x > goal_x + 80:
            running = False; print("🎉 You reached the castle!")

        # Clamp world bounds
        mario_x = max(0, min(WORLD_W - MARIO_W, mario_x))

        # Camera
        camera.update(pg.Rect(mario_x, mario_y, MARIO_W, MARIO_H))

        # Draw
        draw_sky(screen)
        draw_ground(screen, camera.x)
        for bx, by in blocks: draw_block(screen, bx, by, camera.x)
        for c in coins:
            if c[2]: draw_coin(screen, c[0], c[1], camera.x)
        for g in goombas: g.draw(screen, camera.x)

        draw_flag(screen, goal_x, camera.x)
        draw_castle(screen, goal_x + 80, camera.x)
        pg.draw.rect(screen, RED, (mario_x - camera.x, mario_y, MARIO_W, MARIO_H))

        txt = font.render(f"Score: {score}", True, BLACK)
        screen.blit(txt, (10, 10))
        pg.display.flip()

    # End screen
    screen.fill(BLACK)
    msg = "YOU WIN!" if mario_x > goal_x else "GAME OVER"
    text = font.render(msg, True, WHITE)
    screen.blit(text, (SCREEN_W//2 - text.get_width()//2, SCREEN_H//2))
    pg.display.flip()
    pg.time.wait(2000)


if __name__ == "__main__":
    main()
