# Omega City Racer - BEAST MODE 2.0 (Rebuilt for Visual Excellence)
import pygame
import random
import math
import os
import sys

# 1. INITIALIZATION
pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Omega City Racer - Beast Mode")
clock = pygame.time.Clock()

# 2. ROBUST ASSET LOADING (Matching Shadow Strike Logic)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

def create_neon_car(color, size):
    """Procedural fallback car if image fails to load"""
    surf = pygame.Surface(size, pygame.SRCALPHA)
    # Main body
    pygame.draw.rect(surf, color, (0, 0, size[0], size[1]), border_radius=10)
    # Neon outline
    pygame.draw.rect(surf, (255, 255, 255), (0, 0, size[0], size[1]), 3, border_radius=10)
    # Cockpit
    pygame.draw.rect(surf, (0, 0, 0, 150), (size[0]*0.2, size[1]*0.2, size[0]*0.6, size[1]*0.3), border_radius=5)
    # Engine glow
    pygame.draw.rect(surf, (255, 255, 255), (size[0]*0.3, size[1]-10, size[0]*0.4, 10), border_radius=2)
    return surf

def load_asset(filename, size, fallback_color):
    path = os.path.join(ASSETS_DIR, filename)
    try:
        if not os.path.exists(path): raise FileNotFoundError
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except:
        return create_neon_car(fallback_color, size)

# Sprite Sizes
PLAYER_SIZE = (int(W * 0.18), int(W * 0.18 * 1.7))
TRAFFIC_SIZE = (int(W * 0.16), int(W * 0.16 * 1.6))
COIN_SIZE = (int(W * 0.1), int(W * 0.1))

# Load assets or use high-quality procedural fallbacks
player_img = load_asset("player_car.png", PLAYER_SIZE, (0, 200, 255))
traffic_imgs = [
    load_asset("traffic_car_1.png", TRAFFIC_SIZE, (255, 50, 50)),
    load_asset("traffic_car_2.png", TRAFFIC_SIZE, (255, 200, 0))
]
coin_img = load_asset("coin.png", COIN_SIZE, (255, 255, 0))

# Background Assets (Shadow Strike Style)
stars = []
for _ in range(150):
    stars.append([random.randint(0, W), random.randint(0, H), random.randint(1, 4)])

font = pygame.font.SysFont("Arial", int(H * 0.04), True)

# 3. GAME ENGINE
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.px = W // 2 - PLAYER_SIZE[0] // 2
        self.py = H - PLAYER_SIZE[1] - 120
        self.target_x = self.px
        self.score = 0
        self.speed = 15
        self.game_over = False
        self.traffic = []
        self.coins = []
        self.particles = []
        self.shake = 0
        
        for _ in range(4): self.spawn_traffic()
        for _ in range(3): self.spawn_coin()

    def spawn_traffic(self):
        lane = random.randint(0, 2)
        lane_w = W // 3
        x = lane * lane_w + (lane_w - TRAFFIC_SIZE[0]) // 2
        y = random.randint(-H, -200)
        self.traffic.append({"x": x, "y": y, "speed": random.randint(6, 12), "img": random.choice(traffic_imgs)})

    def spawn_coin(self):
        self.coins.append({"x": random.randint(50, W-50), "y": random.randint(-H, -100)})

    def update(self):
        if self.game_over:
            if self.shake > 0: self.shake -= 1
            return

        if self.shake > 0: self.shake -= 1

        # Starfield parallax
        for s in stars:
            s[1] += s[2] + self.speed // 3
            if s[1] > H:
                s[0] = random.randint(0, W)
                s[1] = 0

        # Input (Shadow Strike Style)
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            self.target_x = mx - PLAYER_SIZE[0] // 2
        
        self.px += (self.target_x - self.px) * 0.2
        self.px = max(0, min(W - PLAYER_SIZE[0], self.px))

        # Traffic
        p_rect = pygame.Rect(self.px + 10, self.py + 10, PLAYER_SIZE[0] - 20, PLAYER_SIZE[1] - 20)
        for t in self.traffic[:]:
            t["y"] += t["speed"] + (self.score // 250)
            t_rect = pygame.Rect(t["x"] + 10, t["y"] + 10, TRAFFIC_SIZE[0] - 20, TRAFFIC_SIZE[1] - 20)
            
            if p_rect.colliderect(t_rect):
                self.game_over = True
                self.shake = 20
            
            if t["y"] > H:
                self.traffic.remove(t)
                self.spawn_traffic()
                self.score += 10

        # Coins
        for c in self.coins[:]:
            c["y"] += self.speed
            if math.hypot(self.px + PLAYER_SIZE[0]//2 - c["x"], self.py + PLAYER_SIZE[1]//2 - c["y"]) < 60:
                self.score += 50
                self.coins.remove(c)
                self.spawn_coin()
            elif c["y"] > H:
                self.coins.remove(c)
                self.spawn_coin()

    def draw(self):
        # Screen Shake
        ox = random.randint(-self.shake, self.shake)
        oy = random.randint(-self.shake, self.shake)

        # Draw Space Background
        screen.fill((5, 5, 20))
        for s in stars:
            pygame.draw.circle(screen, (200, 200, 255), (s[0] + ox, s[1] + oy), s[2] // 2)

        # Draw Road Lines (Neon)
        for i in range(1, 3):
            lx = i * (W // 3)
            pygame.draw.line(screen, (50, 50, 100), (lx + ox, 0), (lx + ox, H), 2)

        # Draw entities
        for c in self.coins:
            # Pulsing coin
            pulse = int(5 * math.sin(pygame.time.get_ticks() * 0.01))
            screen.blit(coin_img, (c["x"] - COIN_SIZE[0]//2 + ox + pulse//2, c["y"] - COIN_SIZE[1]//2 + oy + pulse//2))
            
        for t in self.traffic: screen.blit(t["img"], (t["x"] + ox, t["y"] + oy))
        
        # Player Engine Trail
        for _ in range(3):
            tx = self.px + PLAYER_SIZE[0] // 2 + random.randint(-10, 10)
            ty = self.py + PLAYER_SIZE[1] + random.randint(0, 20)
            pygame.draw.circle(screen, (0, 255, 255, 100), (tx + ox, ty + oy), random.randint(5, 15))

        screen.blit(player_img, (self.px + ox, self.py + oy))

        # HUD
        hud_surf = font.render(f"SCORE: {self.score}", True, (0, 255, 255))
        pygame.draw.rect(screen, (0, 0, 0, 150), (10, 10, hud_surf.get_width()+20, 60), border_radius=10)
        screen.blit(hud_surf, (20, 20))

        if self.game_over:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            msg = font.render("SYSTEM CRITICAL: GAME OVER", True, (255, 50, 50))
            retry = font.render("TOUCH TO REBOOT", True, (255, 255, 255))
            screen.blit(msg, (W//2 - msg.get_width()//2, H//2 - 50))
            screen.blit(retry, (W//2 - retry.get_width()//2, H//2 + 20))
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
    clock.tick(60)

pygame.quit()
