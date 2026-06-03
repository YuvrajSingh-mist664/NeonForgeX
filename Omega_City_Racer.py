# Omega City Racer - Beast Mode Edition
import pygame
import random
import math
import os
import sys

# Initialize Pygame
pygame.init()

# Screen Setup - Optimized for Android and Windows
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Omega City Racer - Beast Mode")

clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 40, True)

# Load Assets - Robust path handling for Android
def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

ASSETS_PATH = get_resource_path('assets')

def load_image(name, scale=None):
    path = os.path.join(ASSETS_PATH, name)
    print(f"Attempting to load: {path}")
    try:
        if not os.path.exists(path):
            print(f"FILE NOT FOUND: {path}")
            raise FileNotFoundError
            
        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.smoothscale(img, scale)
        print(f"Successfully loaded: {name}")
        return img
    except Exception as e:
        print(f"FAILED to load {name}: {e}")
        # Fallback to a colored surface if image fails to load
        surf = pygame.Surface(scale if scale else (50, 50))
        surf.fill((255, 0, 255))
        return surf

# Sprite Sizes
PLAYER_SIZE = (int(W * 0.15), int(W * 0.15 * 1.8))
TRAFFIC_SIZE = (int(W * 0.14), int(W * 0.14 * 1.7))
COIN_SIZE = (int(W * 0.08), int(W * 0.08))

player_img = load_image('player_car.png', PLAYER_SIZE)
traffic_imgs = [
    load_image('traffic_car_1.png', TRAFFIC_SIZE),
    load_image('traffic_car_2.png', TRAFFIC_SIZE)
]
coin_img = load_image('coin.png', COIN_SIZE)
road_img = load_image('road_texture.png', (W, H))
bg_img = load_image('city_background.png', (W, H))

# Game State
class Game:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.car_x = W // 2 - PLAYER_SIZE[0] // 2
        self.car_y = H - PLAYER_SIZE[1] - 100
        self.target_x = self.car_x
        self.speed = 15
        self.score = 0
        self.road_offset = 0
        self.traffic = []
        self.coins = []
        self.particles = []
        self.speed_lines = []
        self.shake_intensity = 0
        self.running = True
        self.game_over = False
        
        # Initialize Traffic
        for _ in range(4):
            self.spawn_traffic()
            
        # Initialize Coins
        for _ in range(5):
            self.spawn_coin()

    def spawn_traffic(self):
        lane_width = W // 3
        lane = random.randint(0, 2)
        x = lane * lane_width + (lane_width - TRAFFIC_SIZE[0]) // 2
        y = random.randint(-H, -200)
        speed = random.randint(8, 14)
        img = random.choice(traffic_imgs)
        self.traffic.append({'x': x, 'y': y, 'speed': speed, 'img': img})

    def spawn_coin(self):
        x = random.randint(50, W - 50)
        y = random.randint(-H, -100)
        self.coins.append({'x': x, 'y': y})

    def create_particles(self, x, y, color):
        for _ in range(10):
            self.particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-5, 5),
                'life': 255,
                'color': color
            })

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Android/Touch and Mouse Support
            if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]:
                self.target_x = event.pos[0] - PLAYER_SIZE[0] // 2
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.game_over and event.key == pygame.K_SPACE:
                    self.reset()

        # Smooth Movement
        dx = self.target_x - self.car_x
        self.car_x += dx * 0.2
        self.car_x = max(0, min(W - PLAYER_SIZE[0], self.car_x))

    def update(self):
        if self.game_over:
            if self.shake_intensity > 0:
                self.shake_intensity -= 1
            return

        # Screen Shake decay
        if self.shake_intensity > 0:
            self.shake_intensity -= 1

        # Speed Lines
        if random.random() < 0.3:
            self.speed_lines.append([random.randint(0, W), 0, random.randint(10, 30)])

        for line in self.speed_lines[:]:
            line[1] += 40
            if line[1] > H:
                self.speed_lines.remove(line)

        # Road Animation
        self.road_offset += self.speed
        if self.road_offset >= H:
            self.road_offset = 0

        # Update Traffic
        for t in self.traffic:
            t['y'] += t['speed'] + (self.score // 100) # Difficulty increase
            
            # Collision Detection
            player_rect = pygame.Rect(self.car_x + 10, self.car_y + 10, PLAYER_SIZE[0] - 20, PLAYER_SIZE[1] - 20)
            traffic_rect = pygame.Rect(t['x'] + 5, t['y'] + 5, TRAFFIC_SIZE[0] - 10, TRAFFIC_SIZE[1] - 10)
            
            if player_rect.colliderect(traffic_rect):
                self.create_particles(self.car_x + PLAYER_SIZE[0]//2, self.car_y + PLAYER_SIZE[1]//2, (255, 100, 0))
                self.shake_intensity = 20
                self.game_over = True

            if t['y'] > H:
                self.traffic.remove(t)
                self.spawn_traffic()
                self.score += 5

        # Update Coins
        for c in self.coins:
            c['y'] += self.speed
            
            if math.hypot(self.car_x + PLAYER_SIZE[0]//2 - c['x'], self.car_y + PLAYER_SIZE[1]//2 - c['y']) < 50:
                self.score += 20
                self.create_particles(c['x'], c['y'], (255, 255, 0))
                self.coins.remove(c)
                self.spawn_coin()
            
            elif c['y'] > H:
                self.coins.remove(c)
                self.spawn_coin()

        # Update Particles
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 10
            if p['life'] <= 0:
                self.particles.remove(p)

    def draw(self):
        # Screen Shake Offset
        offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
        offset_y = random.randint(-self.shake_intensity, self.shake_intensity)

        # Background Parallax
        screen.blit(bg_img, (offset_x, offset_y))
        
        # Animated Road
        screen.blit(road_img, (0, self.road_offset))
        screen.blit(road_img, (0, self.road_offset - H))

        # Draw Coins with Glow
        for c in self.coins:
            screen.blit(coin_img, (c['x'] - COIN_SIZE[0]//2, c['y'] - COIN_SIZE[1]//2))

        # Draw Traffic
        for t in self.traffic:
            screen.blit(t['img'], (t['x'], t['y']))

        # Draw Player with Engine Glow
        screen.blit(player_img, (self.car_x, self.car_y))
        # Engine Flame Effect
        flame_h = random.randint(10, 25)
        pygame.draw.ellipse(screen, (0, 200, 255), (self.car_x + PLAYER_SIZE[0]*0.2, self.car_y + PLAYER_SIZE[1], PLAYER_SIZE[0]*0.2, flame_h))
        pygame.draw.ellipse(screen, (0, 200, 255), (self.car_x + PLAYER_SIZE[0]*0.6, self.car_y + PLAYER_SIZE[1], PLAYER_SIZE[0]*0.2, flame_h))

        # Draw Speed Lines
        for line in self.speed_lines:
            pygame.draw.line(screen, (100, 100, 255), (line[0], line[1]), (line[0], line[1] + line[2]), 2)

        # Draw Particles
        for p in self.particles:
            s = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(s, p['color'] + (p['life'],), (5, 5), 5)
            screen.blit(s, (p['x'] + offset_x, p['y'] + offset_y))

        # HUD
        score_txt = font.render(f"NEON SCORE: {self.score}", True, (0, 255, 255))
        screen.blit(score_txt, (20, 20))

        if self.game_over:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            msg = font.render("SYSTEM CRITICAL: GAME OVER", True, (255, 50, 50))
            retry = font.render("TOUCH TO REBOOT", True, (255, 255, 255))
            screen.blit(msg, (W//2 - msg.get_width()//2, H//2 - 50))
            screen.blit(retry, (W//2 - retry.get_width()//2, H//2 + 20))
            
            # Handle restart on touch
            if pygame.mouse.get_pressed()[0]:
                self.reset()

        pygame.display.flip()

# Main Loop
game = Game()
while game.running:
    game.handle_input()
    game.update()
    game.draw()
    clock.tick(60)

pygame.quit()
