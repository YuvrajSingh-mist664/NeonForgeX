# Omega City Racer - NITRO BEAST EDITION
import pygame
import random
import math
import os
import sys

# 1. INITIALIZATION & SMOOTHNESS CONFIG
pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
# Use SCALED for high performance and smooth visuals
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Omega City Racer - Nitro Beast")
clock = pygame.time.Clock()

# 2. ASSET LOADING (Robust & Procedural Fallback)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

def load_asset(filename, size, fallback_color):
    path = os.path.join(ASSETS_DIR, filename)
    try:
        if not os.path.exists(path): raise FileNotFoundError
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, fallback_color, (0, 0, size[0], size[1]), border_radius=12)
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, size[0], size[1]), 2, border_radius=12)
        return surf

PLAYER_SIZE = (int(W * 0.18), int(W * 0.18 * 1.8))
TRAFFIC_SIZE = (int(W * 0.16), int(W * 0.16 * 1.7))
COIN_SIZE = (int(W * 0.1), int(W * 0.1))

player_img = load_asset("player_car.png", PLAYER_SIZE, (0, 200, 255))
traffic_imgs = [
    load_asset("traffic_car_1.png", TRAFFIC_SIZE, (255, 50, 50)),
    load_asset("traffic_car_2.png", TRAFFIC_SIZE, (255, 150, 0))
]
coin_img = load_asset("coin.png", COIN_SIZE, (255, 255, 0))
font = pygame.font.SysFont("Arial", int(H * 0.04), True)

# 3. GAME LOGIC
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.px = W // 2 - PLAYER_SIZE[0] // 2
        self.py = H - PLAYER_SIZE[1] - 150
        self.target_x = self.px
        self.score = 0
        self.base_speed = 12
        self.speed = self.base_speed
        self.nitro = 100 # Nitro fuel (0-100)
        self.is_boosting = False
        self.road_y = 0
        self.game_over = False
        self.traffic = []
        self.coins = []
        self.particles = []
        self.city_lights = []
        
        # Initial city lights for background
        for _ in range(20):
            self.city_lights.append([random.randint(0, W), random.randint(0, H), random.randint(2, 6)])
            
        for _ in range(4): self.spawn_traffic()
        for _ in range(3): self.spawn_coin()

    def spawn_traffic(self):
        lane = random.randint(0, 2)
        lane_w = W // 3
        x = lane * lane_w + (lane_w - TRAFFIC_SIZE[0]) // 2
        y = random.randint(-H, -200)
        self.traffic.append({"x": x, "y": y, "speed": random.randint(5, 10), "img": random.choice(traffic_imgs)})

    def spawn_coin(self):
        self.coins.append({"x": random.randint(50, W-50), "y": random.randint(-H, -100)})

    def update(self):
        if self.game_over: return

        # Input & Nitro (Double Touch or hold to boost)
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed:
            mx, my = pygame.mouse.get_pos()
            self.target_x = mx - PLAYER_SIZE[0] // 2
            # Boost if touching the upper half of the screen
            if my < H // 2 and self.nitro > 0:
                self.is_boosting = True
            else:
                self.is_boosting = False
        else:
            self.is_boosting = False

        # Speed Logic
        if self.is_boosting and self.nitro > 0:
            self.speed = self.base_speed * 2.2
            self.nitro -= 0.8
            # Nitro particles
            for _ in range(2):
                self.particles.append({"x": self.px + PLAYER_SIZE[0]//2, "y": self.py + PLAYER_SIZE[1], 
                                     "vx": random.uniform(-2, 2), "vy": random.uniform(5, 10), "life": 255})
        else:
            self.speed = self.base_speed + (self.score // 500)
            if self.nitro < 100: self.nitro += 0.1 # Refill nitro slowly

        # Road & City Light scrolling
        self.road_y += self.speed
        if self.road_y >= H: self.road_y = 0
        
        for light in self.city_lights:
            light[1] += self.speed * 0.5
            if light[1] > H:
                light[0] = random.randint(0, W)
                light[1] = -10

        # Smooth movement
        self.px += (self.target_x - self.px) * 0.18
        self.px = max(0, min(W - PLAYER_SIZE[0], self.px))

        # Collision & Entity Updates
        p_rect = pygame.Rect(self.px + 15, self.py + 15, PLAYER_SIZE[0] - 30, PLAYER_SIZE[1] - 30)
        
        for t in self.traffic[:]:
            t["y"] += t["speed"] + (self.speed * 0.5)
            t_rect = pygame.Rect(t["x"] + 10, t["y"] + 10, TRAFFIC_SIZE[0] - 20, TRAFFIC_SIZE[1] - 20)
            if p_rect.colliderect(t_rect): self.game_over = True
            if t["y"] > H:
                self.traffic.remove(t)
                self.spawn_traffic()
                self.score += 10

        for c in self.coins[:]:
            c["y"] += self.speed
            if math.hypot(self.px + PLAYER_SIZE[0]//2 - c["x"], self.py + PLAYER_SIZE[1]//2 - c["y"]) < 70:
                self.score += 50
                self.nitro = min(100, self.nitro + 15) # Coins refill nitro!
                self.coins.remove(c)
                self.spawn_coin()
            elif c["y"] > H:
                self.coins.remove(c)
                self.spawn_coin()

        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 15
            if p["life"] <= 0: self.particles.remove(p)

    def draw(self):
        # 1. Background (Dark Neon City Vibes)
        screen.fill((10, 10, 25))
        for light in self.city_lights:
            color = (random.randint(100, 255), 0, random.randint(100, 255))
            pygame.draw.rect(screen, color, (light[0], light[1], light[2], light[2]*4))

        # 2. Neon Road
        for i in range(1, 3):
            lx = i * (W // 3)
            pygame.draw.line(screen, (0, 255, 255, 100), (lx, 0), (lx, H), 2)
        
        # Road markings
        for y in range(-100, H, 100):
            ry = (y + self.road_y) % H
            pygame.draw.rect(screen, (255, 255, 255, 150), (W//2 - 5, ry, 10, 50))

        # 3. Entities
        for p in self.particles:
            pygame.draw.circle(screen, (0, 255, 255, p["life"]), (int(p["x"]), int(p["y"])), random.randint(2, 6))
            
        for c in self.coins:
            screen.blit(coin_img, (c["x"] - COIN_SIZE[0]//2, c["y"] - COIN_SIZE[1]//2))
            
        for t in self.traffic:
            screen.blit(t["img"], (t["x"], t["y"]))

        # 4. Player & Nitro Glow
        if self.is_boosting:
            glow = pygame.Surface((PLAYER_SIZE[0]*1.5, PLAYER_SIZE[1]*1.5), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (0, 255, 255, 80), (0, 0, glow.get_width(), glow.get_height()))
            screen.blit(glow, (self.px - PLAYER_SIZE[0]*0.25, self.py - PLAYER_SIZE[1]*0.25))
            
        screen.blit(player_img, (self.px, self.py))

        # 5. HUD (Beast Mode UI)
        # Nitro Bar
        pygame.draw.rect(screen, (50, 50, 50), (W - 160, 20, 140, 20), border_radius=5)
        pygame.draw.rect(screen, (0, 255, 255), (W - 160, 20, self.nitro * 1.4, 20), border_radius=5)
        nitro_txt = font.render("NITRO", True, (255, 255, 255))
        screen.blit(nitro_txt, (W - 160, 45))

        score_txt = font.render(f"SCORE: {self.score}", True, (0, 255, 255))
        screen.blit(score_txt, (20, 20))

        if self.game_over:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            screen.blit(overlay, (0, 0))
            msg = font.render("ENGINE FAILURE: GAME OVER", True, (255, 50, 50))
            retry = font.render("TOUCH TO REBOOT", True, (255, 255, 255))
            screen.blit(msg, (W//2 - msg.get_width()//2, H//2 - 40))
            screen.blit(retry, (W//2 - retry.get_width()//2, H//2 + 30))
            if pygame.mouse.get_pressed()[0]: self.reset()

        pygame.display.flip()

# 4. MAIN LOOP
game = Game()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
    
    game.update()
    game.draw()
    clock.tick(60) # Locked at 60FPS for smoothness

pygame.quit()
