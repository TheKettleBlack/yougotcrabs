import pygame
from sys import exit
import levels
import copy
import sys
import random

pygame.init()
pygame.display.set_caption("You Got Crabs!")
WIDTH = 1008
HEIGHT = 768
CELLSIZE = 48
BLACK = (63,38,49)

font = pygame.font.Font("font/RasterForgeRegular-JpBgm.ttf", 24)
screen = pygame.display.set_mode((WIDTH,HEIGHT))
iconImage = pygame.image.load("img/favicon.png")
pygame.display.set_icon(iconImage)
splashImg = pygame.image.load("img/splash.png").convert_alpha()
startButton = pygame.image.load("img/btnstart.png").convert_alpha()
restartButton = pygame.image.load("img/btnrestart.png").convert_alpha()
quitButton = pygame.image.load("img/btnquit.png").convert_alpha()
clock = pygame.time.Clock()
levelEnd = False
levelLoaded = False
playerDead = False
playerWon = False
playerGroup = pygame.sprite.GroupSingle()
enemyGroup = pygame.sprite.Group()
terrainGroup = pygame.sprite.Group()
ghostGroup = pygame.sprite.Group()
checkedEnemyGroup = pygame.sprite.Group()
levelReal = 0
splash = True

def drawText(text,font,text_col,x,y):
    img = font.render(text,True,text_col)
    screen.blit(img,(x,y))

def importLevel(levelIndex):
    selectedLevel = copy.deepcopy(levels.gameLevels[levelIndex])
    selectedLevel.insert(0, ["HT"] * 19)
    selectedLevel.append(["HB"] * 19)
    for r, row in enumerate(selectedLevel):
        row.insert(0, "VL")
        row.append("VR")
    selectedLevel[0][0] = "TL"
    selectedLevel[0][-1] = "TR"
    selectedLevel[-1][0] = "BL"
    selectedLevel[-1][-1] = "BR"
    enemyGroup.empty()
    terrainGroup.empty()
    ghostGroup.empty()
    playerGroup.empty()
    for r, row in enumerate(selectedLevel):
        for e, element in enumerate(row):
            if element in (0, 1, "BR", "BL", "TR", "TL", "HT", "HB", "VL", "VR"):
                terrainGroup.add(Terrain(CELLSIZE*e, CELLSIZE*r, element))
            elif element == 2:
                ghostGroup.add(Ghost(CELLSIZE*e, CELLSIZE*r))
            elif element == 8:
                enemyGroup.add(Enemy(CELLSIZE*e, CELLSIZE*r))
            elif element == 9:
                global player
                player = Player(CELLSIZE*e, CELLSIZE*r)
                playerGroup.add(player)

class ParticlePrinciple:
    def __init__(self):
        self.particles = []

    def emit(self):
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                # move, shrink, draw a circle around it
                particle[0][1] += particle[2][0] # move u/d
                particle[0][0] += particle[2][1] # move l/r
                particle[1] -= 0.1
                pygame.draw.circle(screen,particle[3], particle[0], int(particle[1]))

    def add_particles(self):
        pos_x = (WIDTH/2)
        pos_y = (HEIGHT/2)
        radius = random.randint(5, 20)
        direction_x = random.randint(-3,3)
        direction_y = random.randint(-3,3)
        cR = random.randint(0, 255)
        cG = random.randint(0, 255)
        cB = random.randint(0, 255)
        particle_circle = [[pos_x,pos_y], radius, [direction_x, direction_y], (cR, cG, cB)]
        self.particles.append(particle_circle)

    def delete_particles(self):
        particle_copy = [particle for particle in self.particles if particle[1] > 0]
        self.particles = particle_copy

PARTICLE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(PARTICLE_EVENT,50)
particle1 = ParticlePrinciple()

class Button():
    def __init__(self, xButton, yButton, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = xButton
        self.rect.y = yButton
        # self.clicked = False
    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:#: and self.clicked == False:
                # self.clicked = True
                return True

btnStart = Button(670, 182, startButton)
btnRestart = Button(670, 48, restartButton)
btnQuit = Button(670, 158, quitButton)

class Ghost(pygame.sprite.Sprite):
    def __init__(self, xGhost, yGhost):
        super().__init__()
        self.image = pygame.image.load('img/ghost.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = xGhost
        self.rect.y = yGhost

class Enemy(pygame.sprite.Sprite):
    def __init__(self, xEnemy, yEnemy):
        super().__init__()
        self.image = pygame.image.load('img/crab.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = xEnemy
        self.rect.y = yEnemy
    def update(self, xPlayer, yPlayer):
        if self.rect.x < xPlayer and self.rect.y < yPlayer: # this enemy is above and left
            self.rect.x += CELLSIZE
            self.rect.y += CELLSIZE
        elif self.rect.x < xPlayer and self.rect.y > yPlayer: # this enemy is below and left
            self.rect.x += CELLSIZE
            self.rect.y -= CELLSIZE
        elif self.rect.x > xPlayer and self.rect.y < yPlayer: # this enemy is above and right
            self.rect.x -= CELLSIZE
            self.rect.y += CELLSIZE
        elif self.rect.x > xPlayer and self.rect.y > yPlayer: # this enemy is below and right
            self.rect.x -= CELLSIZE
            self.rect.y -= CELLSIZE
        elif self.rect.x < xPlayer and self.rect.y == yPlayer: # this enemy is left
            self.rect.x += CELLSIZE
        elif self.rect.x > xPlayer and self.rect.y == yPlayer: # this enemy is right
            self.rect.x -= CELLSIZE
        elif self.rect.x == xPlayer and self.rect.y < yPlayer: # this enemy is above
            self.rect.y += CELLSIZE
        elif self.rect.x == xPlayer and self.rect.y > yPlayer: # this enemy is below
            self.rect.y -= CELLSIZE

class Player(pygame.sprite.Sprite):
    def __init__(self, xPlayer, yPlayer):
        super().__init__()
        self.image = pygame.image.load('img/player.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = xPlayer
        self.rect.y = yPlayer
    def update(self, pressedKey):
        global levelEnd, playerDead
        if pressedKey == 113: # Q
            self.rect.y -= CELLSIZE
            self.rect.x -= CELLSIZE
        if pressedKey == 119: # W
            self.rect.y -= CELLSIZE
        if pressedKey == 101: # E
            self.rect.x += CELLSIZE
            self.rect.y -= CELLSIZE
        if pressedKey == 97: # A
            self.rect.x -= CELLSIZE
        # if pressedKey == 115: # S
        if pressedKey == 100: # D
            self.rect.x += CELLSIZE
        if pressedKey == 122: # Z
            self.rect.x -= CELLSIZE
            self.rect.y += CELLSIZE
        if pressedKey == 120: # X
            self.rect.y += CELLSIZE
        if pressedKey == 99: # Z
            self.rect.x += CELLSIZE
            self.rect.y += CELLSIZE

        if self.rect.x < CELLSIZE:
            self.rect.x = CELLSIZE
        if self.rect.x > WIDTH - (CELLSIZE * 2):
            self.rect.x = WIDTH - (CELLSIZE * 2)
        if self.rect.y < CELLSIZE:
            self.rect.y = CELLSIZE
        if self.rect.y > HEIGHT - (CELLSIZE * 2):
            self.rect.y = HEIGHT - (CELLSIZE * 2)

        enemyGroup.update(self.rect.x, self.rect.y)

        enemiesToRemove = []
        ghostsToAdd = []
        for enemy in list(enemyGroup):
            hitEnemies = pygame.sprite.spritecollide(enemy, enemyGroup, False)
            hitEnemies = [e for e in hitEnemies if e is not enemy]
            hitGhosts = pygame.sprite.spritecollide(enemy, ghostGroup, False)
            hitPlayer = pygame.sprite.spritecollide(enemy, playerGroup, False)
            if hitEnemies or hitGhosts:
                enemiesToRemove.append(enemy)
                ghostsToAdd.append(Ghost(enemy.rect.x, enemy.rect.y))
            if hitPlayer:
                self.image = pygame.image.load('img/tomb.png').convert_alpha()
                levelEnd = True
                playerDead = True
                enemiesToRemove.append(enemy)
        for ghost in list(ghostGroup):
            hitPlayer = pygame.sprite.spritecollide(ghost, playerGroup, False)
            if hitPlayer:
                self.image = pygame.image.load('img/tomb.png').convert_alpha()
                levelEnd = True
                playerDead = True
        for e in enemiesToRemove:
            enemyGroup.remove(e)
        for g in ghostsToAdd:
            ghostGroup.add(g)
            
class Terrain(pygame.sprite.Sprite):
    def __init__(self,xTerrain,yTerrain,tTerrain):
        super().__init__()
        if tTerrain == 0:
            self.image = pygame.image.load('img/ground1.png').convert_alpha()
        elif tTerrain == "HT":
            self.image = pygame.image.load('img/border_ht.png').convert_alpha()
        elif tTerrain == "HB":
            self.image = pygame.image.load('img/border_hb.png').convert_alpha()
        elif tTerrain == "VL":
            self.image = pygame.image.load('img/border_vl.png').convert_alpha()
        elif tTerrain == "VR":
            self.image = pygame.image.load('img/border_vr.png').convert_alpha()
        elif tTerrain == "TL":
            self.image = pygame.image.load('img/border_tl.png').convert_alpha()
        elif tTerrain == "TR":
            self.image = pygame.image.load('img/border_tr.png').convert_alpha()
        elif tTerrain == "BL":
            self.image = pygame.image.load('img/border_bl.png').convert_alpha()
        elif tTerrain == "BR":
            self.image = pygame.image.load('img/border_br.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = xTerrain
        self.rect.y = yTerrain
        self.type = tTerrain

importLevel(levelReal)
print(len(levels.gameLevels))
while True:
    screen.fill((192,203,220))
    if not splash:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if not levelEnd:
                    if event.key in (pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_a, 
                                    pygame.K_s, pygame.K_d, pygame.K_z, pygame.K_x, pygame.K_c):
                        player.update(event.key)
                else:
                    if event.key == pygame.K_SPACE:
                        if levelReal < len(levels.gameLevels):
                            importLevel(levelReal)
                            player.image = pygame.image.load('img/player.png').convert_alpha()
                            levelEnd = False
                            playerDead = False
        terrainGroup.draw(screen)
        enemyGroup.draw(screen)
        ghostGroup.draw(screen)
        playerGroup.draw(screen)
        if len(enemyGroup) < 1 and not levelEnd and levelReal < len(levels.gameLevels):
            levelEnd = True
            levelReal += 1
        if not levelReal < len(levels.gameLevels):
            drawText("You win!", font, BLACK, 116, 64)
            playerWon = True
            if btnRestart.draw():
                levelReal = 0
                importLevel(levelReal)
                player.image = pygame.image.load('img/player.png').convert_alpha()
                levelEnd = False
                playerDead = False
            if btnQuit.draw():
                pygame.quit()
                exit()
                sys.exit()

            ### START PARTICLE EFFECTS
            if event.type == PARTICLE_EVENT:
                particle1.add_particles()
            particle1.emit()
            ### END PARTICLE EFFECTS

        else:
            drawText(str(levelReal + 1), font, BLACK, 24, 26)
        if levelEnd:
            if playerDead:
                drawText("Level failed", font, BLACK, 780, 26)
                drawText("Press [Space] to continue", font, BLACK, 579, 52)
            else:
                if not playerWon:
                    drawText("Level complete", font, BLACK, 738, 26)
                    drawText("Press [Space] to continue", font, BLACK, 585, 52)
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        screen.blit(splashImg, (0,0))
        if btnStart.draw():
            splash = False
    pygame.display.flip()
    clock.tick(60)

# sound?
# game images sometimes get in the way of text.
# more levels?
# level increments before it actually loads the next level, and displays N+1 on the level cleared screen.