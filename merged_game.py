import pygame
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('RDX Lucky Mega Game')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

player = pygame.Rect(350, 500, 50, 50)
bullets = []
enemies = []
score = 0
lives = 3

for _ in range(5):
    enemies.append(pygame.Rect(random.randint(0, 750), random.randint(-300, -40), 40, 40))

running = True
while running:
    screen.fill((20,20,30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player.x+20, player.y, 10, 20))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.x > 0:
        player.x -= 6
    if keys[pygame.K_RIGHT] and player.x < WIDTH-50:
        player.x += 6
    if keys[pygame.K_UP] and player.y > 0:
        player.y -= 6
    if keys[pygame.K_DOWN] and player.y < HEIGHT-50:
        player.y += 6

    for bullet in bullets[:]:
        bullet.y -= 8
        if bullet.y < 0:
            bullets.remove(bullet)

    for enemy in enemies[:]:
        enemy.y += 4
        if enemy.y > HEIGHT:
            enemy.y = random.randint(-200, -40)
            enemy.x = random.randint(0, 750)
            lives -= 1

        if player.colliderect(enemy):
            enemy.y = random.randint(-200, -40)
            enemy.x = random.randint(0, 750)
            lives -= 1

        for bullet in bullets[:]:
            if bullet.colliderect(enemy):
                score += 10
                enemy.y = random.randint(-200, -40)
                enemy.x = random.randint(0, 750)
                if bullet in bullets:
                    bullets.remove(bullet)

    pygame.draw.rect(screen, (0,255,0), player)

    for bullet in bullets:
        pygame.draw.rect(screen, (255,255,0), bullet)

    for enemy in enemies:
        pygame.draw.rect(screen, (255,0,0), enemy)

    score_text = font.render(f'Score: {score}', True, (255,255,255))
    lives_text = font.render(f'Lives: {lives}', True, (255,255,255))
    screen.blit(score_text, (10,10))
    screen.blit(lives_text, (10,50))

    if lives <= 0:
        game_over = font.render('GAME OVER', True, (255,0,0))
        screen.blit(game_over, (330,280))
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
