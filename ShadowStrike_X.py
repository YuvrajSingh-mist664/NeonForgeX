# ShadowStrike X Omega Plus - Beast Mode
import pygame
import random
import math
import os
import sys

# Initialize Pygame
pygame.init()

# Screen Setup
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("ShadowStrike X - Beast Mode")

clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 36, True)

# Load Assets
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ASSETS_PATH = get_resource_path('assets')

def load_image(name, scale=None):
    path = os.path.join(ASSETS_PATH, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.smoothscale(img, scale)
        return img
    except:
        surf = pygame.Surface(scale if scale else (50, 50))
        surf.fill((255, 0, 255))
        return surf

# Sprite Config
PLAYER_SIZE = (120, 120)
player_img = load_image('player_jet.png', PLAYER_SIZE)

# Game State
class Game:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.px = W // 2
        self.py = H - 200
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.explosions = []
        self.powerups = []
        self.stars = []
        self.score = 0
        self.lives = 5
        self.boss_hp = 0
        self.boss = False
        self.shoot_timer = 0
        self.running = True
        self.game_over = False
        
        for _ in range(100):
            self.stars.append([random.randint(0, W), random.randint(0, H), random.randint(1, 5)])
        for _ in range(8):
            self.spawn_enemy()

    def spawn_enemy(self):
        self.enemies.append([
            random.randint(80, W-80), 
            random.randint(-700, -50), 
            random.randint(3, 7), 
            random.choice(['demon', 'drone', 'eye'])
        ])

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]:
                self.px = max(80, min(W-80, event.pos[0]))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.game_over and event.key == pygame.K_SPACE:
                    self.reset()

    def update(self):
        if self.game_over:
            return

        # Stars
        for s in self.stars:
            s[1] += s[2]
            if s[1] > H:
                s[0] = random.randint(0, W)
                s[1] = 0

        # Shooting
        self.shoot_timer += 1
        if self.shoot_timer >= 5:
            self.bullets.append([self.px, self.py - 50])
            self.shoot_timer = 0

        # Bullets
        for b in self.bullets[:]:
            b[1] -= 20
            if b[1] < 0: self.bullets.remove(b)

        # Enemy Bullets
        for eb in self.enemy_bullets[:]:
            eb[1] += 10
            if math.hypot(self.px - eb[0], self.py - eb[1]) < 50:
                self.lives -= 1
                self.enemy_bullets.remove(eb)
                if self.lives <= 0: self.game_over = True
            elif eb[1] > H:
                self.enemy_bullets.remove(eb)

        # Boss Logic
        if self.score >= 500 and not self.boss:
            self.boss = True
            self.boss_hp = 100
            self.bx, self.by = W // 2, 150

        if self.boss:
            if random.randint(1, 20) == 1:
                self.enemy_bullets.append([self.bx, self.by])
            for b in self.bullets[:]:
                if math.hypot(b[0] - self.bx, b[1] - self.by) < 90:
                    self.boss_hp -= 1
                    self.bullets.remove(b)
                    self.explosions.append([self.bx, self.by, 20])
            if self.boss_hp <= 0:
                self.boss = False
                self.score += 500

        # Enemies
        for en in self.enemies:
            en[1] += en[2]
            if random.randint(1, 60) == 1:
                self.enemy_bullets.append([en[0], en[1]])
            
            if en[1] > H:
                en[0] = random.randint(80, W-80)
                en[1] = random.randint(-500, -50)
                self.lives -= 1
                if self.lives <= 0: self.game_over = True

            if math.hypot(self.px - en[0], self.py - en[1]) < 60:
                self.lives -= 1
                en[1] = -500
                if self.lives <= 0: self.game_over = True

            for b in self.bullets[:]:
                if math.hypot(b[0] - en[0], b[1] - en[1]) < 45:
                    self.score += 10
                    self.explosions.append([en[0], en[1], 25])
                    en[1] = -500
                    self.bullets.remove(b)
                    break

        # Explosions
        for ex in self.explosions[:]:
            ex[2] += 2
            if ex[2] > 50: self.explosions.remove(ex)

    def draw(self):
        screen.fill((5, 5, 20))
        
        # Stars
        for s in self.stars:
            pygame.draw.circle(screen, (200, 200, 255), (s[0], s[1]), s[2] // 2)

        # Player
        # Rotate player image for "core" effect
        angle = (pygame.time.get_ticks() // 10) % 360
        rotated_player = pygame.transform.rotate(player_img, angle)
        rect = rotated_player.get_rect(center=(self.px, self.py))
        screen.blit(rotated_player, rect.topleft)
        
        # Core Glow
        glow_surf = pygame.Surface((150, 150), pygame.SRCALPHA)
        glow_val = int(127 + 127 * math.sin(pygame.time.get_ticks() * 0.01))
        pygame.draw.circle(glow_surf, (0, 255, 255, glow_val // 4), (75, 75), 70)
        screen.blit(glow_surf, (self.px - 75, self.py - 75))

        # Bullets
        for b in self.bullets:
            pygame.draw.rect(screen, (0, 255, 255), (b[0]-3, b[1], 6, 20))

        # Enemy Bullets
        for eb in self.enemy_bullets:
            pygame.draw.circle(screen, (255, 50, 50), (eb[0], eb[1]), 6)

        # Enemies
        for en in self.enemies:
            if en[3] == 'demon':
                pygame.draw.circle(screen, (255, 0, 50), (en[0], en[1]), 35)
            elif en[3] == 'drone':
                pygame.draw.rect(screen, (0, 255, 150), (en[0]-25, en[1]-25, 50, 50))
            else:
                pygame.draw.circle(screen, (150, 0, 255), (en[0], en[1]), 30)

        # Boss
        if self.boss:
            pygame.draw.circle(screen, (255, 0, 0), (self.bx, self.by), 80, 5)
            pygame.draw.rect(screen, (255, 0, 0), (W//2 - 100, 20, self.boss_hp * 2, 15))

        # Explosions
        for ex in self.explosions:
            pygame.draw.circle(screen, (255, 150, 0), (ex[0], ex[1]), ex[2], 2)

        # HUD
        hud_txt = font.render(f"SCORE: {self.score}  LIVES: {self.lives}", True, (0, 255, 255))
        screen.blit(hud_txt, (20, 20))

        if self.game_over:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            msg = font.render("MISSION FAILED", True, (255, 0, 0))
            screen.blit(msg, (W//2 - msg.get_width()//2, H//2))
            if pygame.mouse.get_pressed()[0]: self.reset()

        pygame.display.flip()

# Main
game = Game()
while game.running:
    game.handle_input()
    game.update()
    game.draw()
    clock.tick(60)
pygame.quit()
