# ShadowStrike X Omega Plus Phase 1
import pygame, random, math
pygame.init()
info=pygame.display.Info()
W,H=info.current_w,info.current_h
screen=pygame.display.set_mode((W,H),pygame.FULLSCREEN)
clock=pygame.time.Clock()
font=pygame.font.SysFont('Arial',36,True)

px=W//2
py=H-260
bullets=[]
enemies=[]
enemy_bullets=[]
explosions=[]
powerups=[]
stars=[]
score=0
lives=5
boss_hp=0
boss=False
shoot=0

for i in range(180):
    stars.append([random.randint(0,W),random.randint(0,H),random.randint(1,5)])
for i in range(8):
    enemies.append([random.randint(80,W-80),random.randint(-700,-50),random.randint(3,7),random.choice(['demon','drone','eye'])])

run=True
while run:
    screen.fill((2,2,18))

    for s in stars:
        s[1]+=s[2]
        if s[1]>H:
            s[0]=random.randint(0,W)
            s[1]=0
        pygame.draw.circle(screen,(50,50,100),(s[0],s[1]),s[2]+3)
        pygame.draw.circle(screen,(220,220,255),(s[0],s[1]),s[2])

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            run=False
        if e.type==pygame.MOUSEMOTION:
            px=max(80,min(W-80,e.pos[0]))

    shoot+=1
    if shoot>=3:
        bullets.append([px,py-70])
        shoot=0

    pygame.draw.circle(screen,(0,220,255),(px,py),95,3)
    pygame.draw.polygon(screen,(120,130,170),[(px,py-95),(px-70,py+45),(px+70,py+45)])
    pygame.draw.circle(screen,(0,255,255),(px,py-20),18)
    pygame.draw.polygon(screen,(255,170,0),[(px-18,py+45),(px-2,py+45),(px-10,py+95)])
    pygame.draw.polygon(screen,(255,170,0),[(px+18,py+45),(px+2,py+45),(px+10,py+95)])

    for b in bullets[:]:
        b[1]-=26
        pygame.draw.rect(screen,(0,200,255),(b[0]-5,b[1],10,35))
        if b[1]<0: bullets.remove(b)

    for eb in enemy_bullets[:]:
        eb[1]+=12
        pygame.draw.circle(screen,(255,60,0),(eb[0],eb[1]),6)
        if math.hypot(px-eb[0],py-eb[1])<40:
            lives-=1
            enemy_bullets.remove(eb)
        elif eb[1]>H:
            enemy_bullets.remove(eb)

    if score>=300 and not boss:
        boss=True
        boss_hp=50
        bx=W//2
        by=150

    if boss:
        pygame.draw.circle(screen,(120,0,0),(bx,by),90)
        pygame.draw.circle(screen,(255,0,50),(bx,by),70)
        pygame.draw.circle(screen,(255,255,0),(bx-30,by-20),14)
        pygame.draw.circle(screen,(255,255,0),(bx+30,by-20),14)
        pygame.draw.rect(screen,(80,80,80),(W//2-150,20,300,20))
        pygame.draw.rect(screen,(255,0,0),(W//2-150,20,boss_hp*6,20))

        if random.randint(1,25)==1:
            enemy_bullets.append([bx,by])

        for b in bullets[:]:
            if math.hypot(b[0]-bx,b[1]-by)<90:
                boss_hp-=1
                bullets.remove(b)
                explosions.append([bx,by,20])

        if boss_hp<=0:
            boss=False
            score+=200

    for en in enemies:
        en[1]+=en[2]
        if random.randint(1,90)==1:
            enemy_bullets.append([en[0],en[1]])
        if en[1]>H:
            en[0]=random.randint(80,W-80)
            en[1]=random.randint(-500,-50)
            lives-=1

        if en[3]=='demon':
            pygame.draw.circle(screen,(255,0,50),(en[0],en[1]),40)
        elif en[3]=='drone':
            pygame.draw.rect(screen,(0,255,120),(en[0]-25,en[1]-25,50,50))
        else:
            pygame.draw.circle(screen,(180,0,255),(en[0],en[1]),35)
            pygame.draw.circle(screen,(255,255,255),(en[0],en[1]),12)

        if math.hypot(px-en[0],py-en[1])<60:
            lives-=1
            en[0]=random.randint(80,W-80)
            en[1]=random.randint(-500,-50)

        for b in bullets[:]:
            if math.hypot(b[0]-en[0],b[1]-en[1])<45:
                score+=10
                explosions.append([en[0],en[1],25])
                if random.randint(1,6)==1:
                    powerups.append([en[0],en[1],'life'])
                en[0]=random.randint(80,W-80)
                en[1]=random.randint(-500,-50)
                bullets.remove(b)
                break

    for ex in explosions[:]:
        pygame.draw.circle(screen,(255,120,0),(ex[0],ex[1]),ex[2])
        ex[2]+=3
        if ex[2]>50:
            explosions.remove(ex)

    for p in powerups[:]:
        p[1]+=5
        pygame.draw.circle(screen,(0,255,0),(p[0],p[1]),15)
        if math.hypot(px-p[0],py-p[1])<45:
            if p[2]=='life' and lives<5:
                lives+=1
            powerups.remove(p)

    hud=pygame.Surface((340,110),pygame.SRCALPHA)
    hud.fill((0,0,0,140))
    screen.blit(hud,(10,10))
    pygame.draw.rect(screen,(0,255,255),(10,10,340,110),3,border_radius=18)
    screen.blit(font.render(f'SCORE {score}',True,(0,255,255)),(25,20))

    for i in range(lives):
        pygame.draw.circle(screen,(255,40,80),(45+i*40,90),13)
        pygame.draw.circle(screen,(255,90,130),(55+i*40,90),13)
        pygame.draw.polygon(screen,(255,60,90),[(36+i*40,95),(64+i*40,95),(50+i*40,115)])

    if lives<=0:
        txt=font.render('GAME OVER',True,(255,0,0))
        screen.blit(txt,(W//2-120,H//2))
        pygame.display.flip()
        pygame.time.delay(3000)
        run=False

    pygame.display.flip()
    clock.tick(60)
pygame.quit()