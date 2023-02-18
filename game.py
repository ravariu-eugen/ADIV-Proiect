import serial
import pygame
import random

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_COLOR = (255, 255, 255)
FRAME_RATE = 160

PLAYER_START = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
PLAYER_SIZE = (100,100)
ACCEL_FACTOR = 3
FRICTION = 0.08
BOUNCE = 0.8

ENEMY_SIZE = (30, 10)
SPAWN_RATE = 4
ENEMY_SPEED_MIN = 5
ENEMY_SPEED_MAX = 9


from pygame.locals import (
    K_DOWN,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
class Player(pygame.sprite.Sprite):

    def __init__(self, poz):
        super(Player, self).__init__()
        self.surf = pygame.image.load("ship.png").convert()
        self.surf = pygame.transform.scale(self.surf, PLAYER_SIZE)
        self.rect = self.surf.get_rect(center=poz)
        self.vX = 0
        self.vY = 0
    def update(self, aX, aY):
        # actualizare pozitie
        self.vX += (aX - self.vX * FRICTION)
        self.vY += (aY - self.vY * FRICTION)
        self.rect.move_ip(self.vX, self.vY)

        # reflectare in caz de contact cu marginea
        if self.rect.left < 0:
            self.rect.left = 0
            self.vX = -self.vX * BOUNCE
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.vX = -self.vX * BOUNCE
        if self.rect.top < 0:
            self.rect.top = 0
            self.vY = -self.vY * BOUNCE
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vY = -self.vY * BOUNCE

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("laser.png").convert()
        self.surf = pygame.transform.scale(self.surf, ENEMY_SIZE)
        
        match random.randint(0,3): # alegere orientare
            case 0:
                self.surf =pygame.transform.rotate(self.surf, 90)
                self.rect = self.surf.get_rect(
                    center=(random.randint(0, SCREEN_WIDTH), -50)
                )
                self.speedX = 0
                self.speedY = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
            case 1:
                self.rect = self.surf.get_rect(
                    center=(SCREEN_WIDTH + 50,random.randint(0, SCREEN_HEIGHT))
                )
                self.speedX = -random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
                self.speedY = 0
            case 2:
                self.surf =pygame.transform.rotate(self.surf, 90)
                self.rect = self.surf.get_rect(
                    center=(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50)
                )
                self.speedX = 0
                self.speedY = -random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
            case 3:
                self.rect = self.surf.get_rect(
                    center=(-50, random.randint(0, SCREEN_HEIGHT))
                )
                self.speedX = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
                self.speedY = 0

    
    
    def update(self): 
        # actualizare pozitie
        self.rect.move_ip(self.speedX, self.speedY)
        # daca ajung la margine, sunt distruse
        if self.rect.right < -100:
            self.kill()
        if self.rect.left > SCREEN_WIDTH+100:
            self.kill()
        if self.rect.bottom < -100:
            self.kill()
        if self.rect.top > SCREEN_HEIGHT+100:
            self.kill()

def get_data(): 
    ser.write(b'0')
    line1 = ser.readline()   
    while (line1 == b''): # trimite octeti pana cand primeste un raspuns
        ser.write(b'0')
        print("08")
        line1 = ser.readline()
    v1 = line1.split()
    ax = float(v1[1].decode("utf-8"))
    ay = float(v1[2].decode("utf-8"))
    az = float(v1[3].decode("utf-8"))
    print("AX : %5.2f AY : %5.2f AZ : %5.2f" % (ax,ay,az))
    line2 = ser.readline()   
    v1 = line2.split()
    gx = float(v1[1].decode("utf-8"))
    gy = float(v1[2].decode("utf-8"))
    gz = float(v1[3].decode("utf-8"))
    print("GX : %5.2f GY : %5.2f GZ : %5.2f" % (gx,gy,gz))
    return ax,ay,az,gx,gy,gz


#initializare joc
pygame.init()
clock = pygame.time.Clock()
ser = serial.Serial('COM5', 9600, timeout=1)
font = pygame.font.Font('freesansbold.ttf', 32)

#initializare fereastra
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption('Game')

#eveniment creare proiectil
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, int(1000/SPAWN_RATE))


player = Player(PLAYER_START)
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

passed_time = 0
timer_started = False

best_time = 0

running = True
fail = False
while(running):
    #colorare fundal
    screen.fill(SCREEN_COLOR)

    
    if not timer_started:
        # incepere cronometru
        timer_started = True
        start_time = pygame.time.get_ticks()
    else:
        # actualizare cronometru
        passed_time = pygame.time.get_ticks() - start_time
        
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False # inchidere program

        elif event.type == QUIT:
            running = False # inchidere program

        elif event.type == ADDENEMY:
            # creare nou proiectil
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)
    ax,ay,az,gx,gy,gz = get_data()


    
    player.update(ACCEL_FACTOR*ay, ACCEL_FACTOR*ax)
    enemies.update()
    # desenare entitati
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)


    timer_text = font.render(str(passed_time/1000), True, (0,0,0))
    screen.blit(timer_text, (20, 50))
    best_time = max(best_time, passed_time)
    timer_text = font.render('BEST:'+str(best_time/1000), True, (0,0,0))
    screen.blit(timer_text, (20, 100))
    if pygame.sprite.spritecollideany(player, enemies):
        # a avut loc un contact, deci jucatorul e inlaturat
        player.kill()
        fail = True
        timer_started = False
    while(fail):
        #daca jucatorul a pierdut
        for x in all_sprites:
            x.kill()
        running = False
        screen.fill(SCREEN_COLOR)
        timer_text = font.render(str(passed_time/1000), True, (0,0,0))
        screen.blit(timer_text, (20, 50))
        timer_text = font.render('BEST:'+str(best_time/1000), True, (0,0,0))
        screen.blit(timer_text, (20, 100))
        failText = font.render('YOU FAILED - PRESS DOWN TO RESET', True, (0,0,0))
        textRect = failText.get_rect()
        textRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        screen.blit(failText, textRect)
        pygame.display.flip()
        for event in pygame.event.get():
    
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    fail = False # inchidere program
                elif event.key == K_DOWN:
                    fail = False # reincepere joc
                    running = True
                    player = Player(PLAYER_START)
                    all_sprites.add(player)

            elif event.type == QUIT:
                fail = False # inchidere program
    #afisare ecran
    pygame.display.flip()
    clock.tick(FRAME_RATE)
pygame.quit()
ser.close()