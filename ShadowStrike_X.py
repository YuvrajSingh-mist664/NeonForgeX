import pygame, random, math

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('ShadowStrike X Omega')
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 38, bold=True)

player_x=WIDTH//2
player_y=HEIGHT-320
bullets=[]
enemies=[]
stars=[]
score=0
lives=5
shoot_timer=0
pulse=0

for i in range(150):
    stars.append([random.randint(0,WIDTH),random.randint(0,HEIGHT),random.randint(1,4)])

for i in range(8):
    enemies.append([random.randint(80,WIDTH-80),random.randint(-800,-50),random.randint(4,7)])

running=True
while running:
    screen.fill((2,2,18))
    pulse=(pulse+1)%60
    glow=5+abs(30-pulse)//4

    for s in stars:
        s[1]+=s[2]
        if s[1]>HEIGHT:
            s[0]=random.randint(0,WIDTH)
            s[1]=0
        pygame.draw.circle(screen,(80,80,180),(s[0],s[1]),s[2]+2)
        pygame.draw.circle(screen,(230,230,255),(s[0],s[1]),s[2])

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if event.type==pygame.MOUSEMOTION:
            x,y=event.pos
            player_x=max(70,min(WIDTH-70,x))

    shoot_timer+=1
    if shoot_timer>=8:
        bullets.append([player_x,player_y-75])
        shoot_timer=0

    # Futuristic Jet
    pygame.draw.circle(screen,(0,220,255),(player_x,player_y),90,4)
    pygame.draw.circle(screen,(0,120,255),(player_x,player_y),70,2)
    pygame.draw.polygon(screen,(120,130,170),[(player_x,player_y-95),(player_x-70,player_y+45),(player_x+70,player_y+45)])
    pygame.draw.polygon(screen,(60,80,110),[(player_x-90,player_y+20),(player_x-25,player_y+5),(player_x-35,player_y+55)])
    pygame.draw.polygon(screen,(60,80,110),[(player_x+90,player_y+20),(player_x+25,player_y+5),(player_x+35,player_y+55)])
    pygame.draw.circle(screen,(0,255,255),(player_x,player_y-25),18)
    pygame.draw.line(screen,(0,255,255),(player_x-45,player_y+10),(player_x+45,player_y+10),4)
    pygame.draw.polygon(screen,(255,170,0),[(player_x-20,player_y+45),(player_x-5,player_y+45),(player_x-12,player_y+95)])
    pygame.draw.polygon(screen,(255,170,0),[(player_x+20,player_y+45),(player_x+5,player_y+45),(player_x+12,player_y+95)])

    for b in bullets[:]:
        b[1]-=26
        pygame.draw.rect(screen,(0,120,255),(b[0]-7,b[1],14,40))
        pygame.draw.rect(screen,(255,255,255),(b[0]-2,b[1],4,40))
        if b[1]<0:
            bullets.remove(b)

    for e in enemies:
        e[1]+=e[2]
        if e[1]>HEIGHT:
            e[0]=random.randint(80,WIDTH-80)
            e[1]=random.randint(-500,-50)
            lives-=1

        # Terror Monster
        pygame.draw.circle(screen,(120,0,0),(e[0],e[1]),48)
        pygame.draw.circle(screen,(255,0,50),(e[0],e[1]),38)
        pygame.draw.polygon(screen,(50,0,0),[(e[0]-35,e[1]-40),(e[0]-15,e[1]-80),(e[0]-5,e[1]-35)])
        pygame.draw.polygon(screen,(50,0,0),[(e[0]+35,e[1]-40),(e[0]+15,e[1]-80),(e[0]+5,e[1]-35)])
        pygame.draw.circle(screen,(255,255,0),(e[0]-15,e[1]-10),8)
        pygame.draw.circle(screen,(255,255,0),(e[0]+15,e[1]-10),8)
        pygame.draw.circle(screen,(0,0,0),(e[0]-15,e[1]-10),3)
        pygame.draw.circle(screen,(0,0,0),(e[0]+15,e[1]-10),3)
        for t in range(-20,25,10):
            pygame.draw.polygon(screen,(255,255,255),[(e[0]+t,e[1]+18),(e[0]+t+6,e[1]+35),(e[0]+t+12,e[1]+18)])

        if math.hypot(player_x-e[0],player_y-e[1])<70:
            lives-=1
            e[0]=random.randint(80,WIDTH-80)
            e[1]=random.randint(-500,-50)

        for b in bullets[:]:
            if math.hypot(b[0]-e[0],b[1]-e[1])<48:
                score+=10
                e[0]=random.randint(80,WIDTH-80)
                e[1]=random.randint(-500,-50)
                if b in bullets:
                    bullets.remove(b)

    hud=pygame.Surface((330,110),pygame.SRCALPHA)
    hud.fill((0,0,0,140))
    screen.blit(hud,(15,15))
    pygame.draw.rect(screen,(0,255,255),(15,15,330,110),3,border_radius=18)
    score_glow=font.render(f'SCORE {score}',True,(0,120,255))
    score_text=font.render(f'SCORE {score}',True,(0,255,255))
    screen.blit(score_glow,(33,31))
    screen.blit(score_text,(30,28))

    for i in range(lives):
        pygame.draw.circle(screen,(255,40,80),(45+i*40,95),13)
        pygame.draw.circle(screen,(255,90,130),(55+i*40,95),13)
        pygame.draw.polygon(screen,(255,60,90),[(36+i*40,100),(64+i*40,100),(50+i*40,120)])

    if lives<=0:
        over=font.render('GAME OVER',True,(255,80,80))
        screen.blit(over,(WIDTH//2-120,HEIGHT//2))
        pygame.display.flip()
        pygame.time.delay(3000)
        running=False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()