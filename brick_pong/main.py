import pygame
from pygame.locals import *
import sys
import os.path
from pygame.math import Vector2
import math
from random import randint, choices
import time

pathFile = os.path.dirname(__file__)

pygame.init()
WIDTH = 600
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

def map(n, start1, stop1, start2, stop2):
    return (n - start1) / (stop1 - start1) * (stop2 - start2) + start2

def clamp(n: float, minVal: float, maxVal: float) -> float:
    return min(maxVal, max(minVal, n))

def drawText(text: str, pos: Vector2, fontSize: int=18, fontType: str="comicsans", bold: bool=False,
             italic: bool=False, antiAlias: bool=False, textColor: tuple=BLACK, bgColor: tuple=None,
             centerX: float=0, centerY: float=0, surface: pygame.Surface=window):
    font = pygame.font.SysFont(fontType, fontSize, bold, italic)
    textSurface = font.render(text, antiAlias, textColor, bgColor)
    textRect = textSurface.get_rect()
    surface.blit(textSurface, [pos.x + (textRect.width/2) * centerX, pos.y + (textRect.height/2) * centerY])

def addBall():
    if len(balls) < maxBalls:
        balls.append(Ball(Vector2(movePad.pos.x, initialBallPos.y), Vector2(randint(-2, 2), -1), ballSpeed, ballRadius, ballColor, ballSprite))

    if debugMode:
        print(len(balls))

class Brick:
    def __init__(self, pos: Vector2, size: Vector2, health: int=1, color: tuple=BLACK, textureFile: str=None, isMovePad: bool=False) -> None:
        self.pos = pos
        self.width = size.x
        self.height = size.y
        self.color = color
        self.textureFile = textureFile
        self.maxHealth = health
        self.health = self.maxHealth
        self.isMovePad = isMovePad
        if self.textureFile:
            # Load sprite
            self.brickSprite = pygame.image.load(os.path.join(pathFile, self.textureFile)).convert_alpha().convert()
            self.brickSprite = pygame.transform.scale(self.brickSprite, (self.width, self.height))

    def draw(self, surface: pygame.Surface=window, drawOutline: bool=True) -> None:
        if self.health <= 0 and not self.isMovePad:
            return

        if self.textureFile:
            # Draw damage on top of brick
            healthRatio = self.health / self.maxHealth
            percentPerDamageLevel = 1 / (len(damageSprites) + 1)
            if healthRatio <= 1 - percentPerDamageLevel:
                idx = map(self.health, 0, self.maxHealth, 0, len(damageSprites))                
                damageSprite = pygame.image.load(os.path.join(pathFile, f"{damageSprites[math.floor(idx)]}")).convert_alpha()
                damageSprite = pygame.transform.scale(damageSprite, (self.width, self.height))
                #print(f"IndexError with index {idx} for health: {self.health}")
                self.brickSprite.blit(damageSprite, (0, 0))

            # Draw brick's health if debug mode is activated
            if debugMode:
                drawText(str(self.health), Vector2(self.brickSprite.get_width()/2, self.brickSprite.get_height()/2), bold=True, textColor=GREEN, centerX=-1, centerY=-1, surface=self.brickSprite)
            
            # Draw sprite on screen
            surface.blit(self.brickSprite, (self.pos.x - self.width/2, self.pos.y - self.height/2))

        else:
            # Draw the rect
            pygame.draw.rect(surface, self.color, (self.pos.x - self.width/2, self.pos.y - self.height/2, self.width, self.height))
            
            # Draw outlines
            if drawOutline:
                pygame.draw.rect(surface, brickOutlineColor, (self.pos.x - self.width/2, self.pos.y - self.height/2, self.width, self.height), brickOutlineWidth)

            # Draw the brick current health
            if not self.isMovePad:# and debugMode:
                drawText(str(self.health), self.pos, bold=True, textColor=GREEN, centerX=-1, centerY=-1, surface=surface)

    def onHit(self) -> None:
        self.health -= 1
        if not self.isMovePad and self.health == 0 and randint(0, 1000)/1000 < powerupDropChance:
            powerupType = choices(possiblePowerups, powerupWeights, k=1)[0]
            powerups.append(Powerup(Vector2(self.pos.x, self.pos.y), powerupType=powerupType,
                            color=powerupColors[powerupType], duration=randint(4, 7), fallSpeed=randint(1, 4)))
            
class Ball:
    def __init__(self, pos: Vector2, vel: Vector2, speed: float=3, radius: int=15, color: tuple=RED,
                 textureFile: str='') -> None:
        self.pos = pos
        self.vel = vel.normalize()
        self.color = color
        self.radius = radius
        self.speed = speed
        self.ballSprite = None
        if textureFile:
            self.ballSprite = pygame.image.load(os.path.join(pathFile, textureFile)).convert_alpha()
            self.ballSprite = pygame.transform.scale(self.ballSprite, (self.radius*2, self.radius*2))
    
    def update(self) -> bool:
        if self.vel.x == 0:
            self.vel.x += .1
        if self.vel.y == 0:
            self.vel.y += .1
        # Calculate steps of physics simulation
        global dt
        stepDT = dt / ballPhysicsSteps
        for _ in range(ballPhysicsSteps):
            # Calculate next position
            targetPos = self.pos + self.vel.normalize() * self.speed * speedMult * stepDT

            if targetPos.y > HEIGHT - self.radius:
                # Eliminate this ball
                return True

            # Collision with borders
            if targetPos.x < self.radius or targetPos.x > WIDTH - self.radius:
                self.vel.x *= -1
            if targetPos.y < self.radius or targetPos.y > HEIGHT - self.radius:
                self.vel.y *= -1

            # Get the smallest possible area to check collisions for performance
            areaTL = Vector2(0, 0)
            areaTL.x = min(self.pos.x, targetPos.x)
            areaTL.y = min(self.pos.y, targetPos.y)
            areaTL -= Vector2(self.radius, self.radius) * 2
            areaTL.x = max(areaTL.x, 0)
            areaTL.y = max(areaTL.y, 0)
            areaBR = Vector2(0, 0)
            areaBR.x = max(self.pos.x, targetPos.x)
            areaBR.y = max(self.pos.y, targetPos.y)
            areaBR += Vector2(self.radius, self.radius) * 2
            areaBR.x = min(areaBR.x, WIDTH)
            areaBR.y = min(areaBR.y, HEIGHT)

            # Check collision for all bricks in the calculated area
            for brick in bricks + [movePad]:
                if clamp(brick.pos.x, areaTL.x - brick.width/2, areaBR.x + brick.width/2) == brick.pos.x and clamp(brick.pos.y, areaTL.y - brick.height/2, areaBR.y + brick.height/2) == brick.pos.y:
                    # Calculate
                    nearestPoint = Vector2()
                    nearestPoint.x = max(brick.pos.x - brick.width/2, min(targetPos.x, brick.pos.x + brick.width/2))
                    nearestPoint.y = max(brick.pos.y - brick.height/2, min(targetPos.y, brick.pos.y + brick.height/2))

                    rayToNearest = nearestPoint - targetPos
                    try:
                        overlap = self.radius  - rayToNearest.magnitude()
                    except ZeroDivisionError:
                        overlap = 0

                    if overlap > 0:
                        brick.onHit()
                        try:
                            normalized = rayToNearest.normalize()
                        except ValueError:
                            normalized = rayToNearest

                        # Displace back by overlap
                        self.pos -= normalized * overlap

                        # Adjust velocity when the rotation degree is horizontal or vertical
                        deg = math.degrees(math.atan2(normalized.y, normalized.x))
                        if abs(deg - 90) < .1 or abs(deg + 90) < .1:
                            # Calculate normal of face and reflect
                            if abs(nearestPoint.y - brick.pos.y - brick.height/2) < .1:
                                # Right wall
                                # Calculate normal of left/right wall
                                start = Vector2(brick.pos.x - brick.width/2, brick.pos.y - brick.height/2)
                                end = Vector2(brick.pos.x + brick.width/2, brick.pos.y - brick.height/2)
                                direc = (end - start).normalize()
                                normal = Vector2(-direc.y, direc.x)
                                self.vel.reflect_ip(normal)
                            elif abs(nearestPoint.y - brick.pos.y + brick.height/2) < .1:
                                # Left wall
                                start = Vector2(brick.pos.x - brick.width/2, brick.pos.y + brick.height/2)
                                end = Vector2(brick.pos.x + brick.width/2, brick.pos.y + brick.height/2)
                                direc = (end - start).normalize()
                                normal = Vector2(-direc.y, direc.x)
                                self.vel.reflect_ip(normal)
                        elif abs(deg - 180) < .1 or deg < .1:
                            if abs(nearestPoint.x - brick.pos.x - brick.width/2) < .1:
                                # Right wall
                                # Calculate normal of right wall
                                start = Vector2(brick.pos.x - brick.width/2, brick.pos.y - brick.height/2)
                                end = Vector2(brick.pos.x - brick.width/2, brick.pos.y + brick.height/2)
                                direc = (end - start).normalize()
                                normal = Vector2(-direc.y, direc.x)
                                self.vel.reflect_ip(normal)
                            elif abs(nearestPoint.x - brick.pos.x + brick.width/2) < .1:
                                # Left wall
                                start = Vector2(brick.pos.x + brick.width/2, brick.pos.y - brick.height/2)
                                end = Vector2(brick.pos.x + brick.width/2, brick.pos.y + brick.height/2)
                                direc = (end - start).normalize()
                                normal = Vector2(-direc.y, direc.x)
                                self.vel.reflect_ip(normal)
                        else:
                            self.vel = -normalized

                        #self.vel = -normalized
                        targetPos = targetPos - normalized * overlap

            if debugMode:
                pygame.draw.rect(window, GREEN, (areaTL.x, areaTL.y, areaBR.x - areaTL.x, areaBR.y - areaTL.y), 0)

            self.pos = self.pos + self.vel * self.speed * speedMult * stepDT

        return False

    def draw(self, surface: pygame.Surface=window) -> None:
        if self.ballSprite:
            surface.blit(self.ballSprite, (self.pos.x - self.radius, self.pos.y - self.radius))
        else:
            pygame.draw.circle(surface, self.color, (self.pos.x, self.pos.y), self.radius)

class Powerup:
    def __init__(self, pos: Vector2, radius: int=15, fallSpeed: float=1, powerupType: str="fastBall", duration: float=3, color: tuple=BLACK) -> None:
        '''Creates a powerup.

        Powerup Type can be:
         - fastBall
         - slowBall
         - bigPad
         - smallPad
         - addBall
        '''
        self.pos = pos
        self.radius = radius
        self.fallSpeed = fallSpeed
        self.duration = duration
        self.__startTime = None
        self.powerupType = powerupType
        self.color = color
        self.started = False
        self.__initialState = None

    def touchedMovePad(self) -> bool:
        nearestPoint = Vector2()
        nearestPoint.x = max(movePad.pos.x - movePad.width/2, min(self.pos.x, movePad.pos.x + movePad.width/2))
        nearestPoint.y = max(movePad.pos.y - movePad.height/2, min(self.pos.y, movePad.pos.y + movePad.height/2))

        rayToNearest = nearestPoint - self.pos
        try:
            overlap = self.radius - rayToNearest.magnitude()
        except ZeroDivisionError:
            overlap = 0

        return overlap > 0

    def update(self) -> bool:
        '''
        Updates position based on fallSpeed and returns whether it touched the ground or not
        '''
        self.pos += Vector2(0, self.fallSpeed)

        if self.pos.y > HEIGHT - self.radius:
            return True

        return False

    def isDone(self) -> bool:
        return time.time() > self.__startTime + self.duration

    def start(self) -> None:
        if self.started:
            return
        self.started = True

        global speedMult
        self.__startTime = time.time()

        if self.powerupType.lower() == "fastball":
            self.__initialState = speedMult
            speedMult = speedMult * fastBallSpeedMult
        elif self.powerupType.lower() == "slowball":
            self.__initialState = speedMult
            speedMult = speedMult / slowBallSpeedMult
        elif self.powerupType.lower() == "bigpad":
            self.__initialState = movePad.width
            movePad.width *= bigPadSizeMult
        elif self.powerupType.lower() == "smallpad":
            self.__initialState = movePad.width
            movePad.width /= smallPadSizeMult
        elif self.powerupType.lower() == "addball":
            addBall()
        else:
            raise ValueError(f"No such powerupType \"{self.powerupType}\"")

    def end(self) -> None:
        if not self.started:
            return

        global speedMult

        if self.powerupType.lower() == "fastball":
            #speedMult = self.__initialState
            speedMult = speedMult / fastBallSpeedMult
        elif self.powerupType.lower() == "slowball":
            #speedMult = self.__initialState]
            speedMult = speedMult * slowBallSpeedMult
        elif self.powerupType.lower() == "bigpad":
            #movePad.width = self.__initialState
            movePad.width = movePad.width / bigPadSizeMult
        elif self.powerupType.lower() == "smallpad":
            movePad.width = movePad.width * smallPadSizeMult
            #movePad.width = self.__initialState

    def draw(self, surface: pygame.Surface=window) -> None:
        pygame.draw.circle(surface, self.color, (self.pos.x, self.pos.y), self.radius)

# Texture paths
brickSprites = [
    "images/black.png",
    "images/blue.png",
    "images/green.png",
    "images/orange.png",
    "images/purple.png",
    "images/red.png",
    "images/yellow.png"
]
damageSprites = [
    "images/damaged3.png",
    "images/damaged2.png",
    "images/damaged1.png",
]
ballSprite = "images/ball.png"

# States
debugMode = False
movementWithKeyboard = False
generateFullLevel = False
generateRandomLevel = True
brickChance = .4

# Move Pad
movePadGroundDistance = 50
movePadW = 80
movePadH = 15
movePad = Brick(Vector2(WIDTH/2, HEIGHT - movePadGroundDistance), Vector2(movePadW, movePadH), color=BLACK, isMovePad=True)
moveSpeed = 3
xMove = 0

# Bricks info
brickCols = 10
brickRows = 10
maxBrickYpos = HEIGHT/2
brickW = WIDTH / brickCols
brickH = maxBrickYpos / brickRows

# Levels Configuration
bricks: list[Brick] = []
brickOutlineColor = (0, 255, 255)
brickOutlineWidth = 1
brickChar = "#"
level1 = [
    '##########',
    '#........#',
    '#..#..#..#',
    '#..#..#..#',
    '#........#',
    '#.#....#.#',
    '#..#..#..#',
    '#...##...#',
    '#........#',
    '##########',
]
level2 = [
    '##########',
    '#........#',
    '#..#..#..#',
    '#..#..#..#',
    '#........#',
    '#...##...#',
    '#..#..#..#',
    '#.#....#.#',
    '#........#',
    '##########',
]
level3 = [
    '..........',
    '....##....',
    '...#..#...',
    '...#..#...',
    '...#..#...',
    '...#..#...',
    '..#....#..',
    '.#..##..#.',
    '..##..##..',
    '..........',
]
chosenMap = level1

# Setup level
for i in range(brickCols):
    for j in range(brickRows):

        # Get the char from the bricks map
        try:
            char = chosenMap[j][i]
        # If out of bounds, just don't do anything
        except IndexError:
            char = brickChar*2
        if (not generateRandomLevel and char == brickChar) or (generateRandomLevel and randint(0, 1000)/1000 < brickChance) or generateFullLevel:
            x = WIDTH/brickCols * i
            y = maxBrickYpos/brickRows * j
            sprite = brickSprites[randint(0, len(brickSprites)-1)]
            bricks.append(Brick(Vector2(x + brickW/2, y + brickH/2), Vector2(brickW, brickH), textureFile=sprite, health=randint(1, 4)))

# Balls configuration
ballSpeed = 150
ballPhysicsSteps = 1
speedMult = 1
ballRadius = 13
ballColor = RED
initialBallPos = Vector2(WIDTH/2, HEIGHT - movePadGroundDistance - 50)
initialBallVel = Vector2(randint(-100, 100)/100, -1)
balls: list[Ball] = []
balls.append(Ball(initialBallPos, initialBallVel, ballSpeed, ballRadius, ballColor, ballSprite))

# Powerups
powerupWeights = [
    1.5,    # Slow Ball
    1.3,    # Fast Ball
    .6,     # Big Pad
    .8,     # Small Pad
    .4      # Add Ball
]
powerupColors = {
    'slowBall': (50, 150, 255),     # Blue
    'fastBall': YELLOW,
    'bigPad': GREEN,
    'smallPad': RED,
    'addBall': (100, 0, 100)        # Purple
}
powerupDropChance = .45
possiblePowerups = [
    'slowBall',
    'fastBall',
    'bigPad',
    'smallPad',
    'addBall'
]
maxBalls = 500
fastBallSpeedMult = 2
slowBallSpeedMult = 2.5
bigPadSizeMult = 1.8
smallPadSizeMult = 1.7
powerups: list[Powerup] = []

dt = 1/FPS
while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)
    
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in (K_a, K_LEFT):
                xMove -= 1
            elif event.key in (K_d, K_RIGHT):
                xMove += 1
            elif event.key == K_e:
                addBall()
        elif event.type == KEYUP:
            if event.key in (K_a, K_LEFT):
                xMove += 1
            elif event.key in (K_d, K_RIGHT):
                xMove -= 1

    # Clear screen
    window.fill(WHITE)

    # Update powerups
    for powerup in powerups[:]:
        if not powerup.started:
            if powerup.touchedMovePad():
                # Touched movePad, so start the powerup
                powerup.start()
            else:
                # Didn't touch, so draw the powerup
                hitGround = powerup.update()
                if hitGround:
                    powerups.remove(powerup)

        # Check if it's done (duration ended)
        if powerup.started and powerup.isDone():
            powerup.end()
            powerups.remove(powerup)

    # Update pad position
    if movementWithKeyboard:
        movePad.pos.x = clamp(movePad.pos.x + xMove * moveSpeed, movePad.width/2, WIDTH - movePad.width/2)
    else:
        movePad.pos.x = clamp(mouseX, movePad.width/2, WIDTH - movePad.width/2)

    # Draw the player pad
    movePad.draw(drawOutline=False)

    # Update and draw bricks
    for brick in bricks[:]:
        if brick.health <= 0:
            bricks.remove(brick)

    # Update balls
    for ball in balls[:]:
        touchedGround = ball.update()
        if touchedGround:
            balls.remove(ball)

    # Draw bricks
    for brick in bricks:
        brick.draw()

    # Draw all balls
    for ball in balls:
        ball.draw()

    # Draw powerups
    for powerup in powerups:
        if not powerup.started:
            powerup.draw()

    # Draw FPS
    drawText(f"FPS: {clock.get_fps():.0f}", Vector2(), fontSize=25, textColor=RED)
    print(dt)

    pygame.display.update()
    dt = clock.tick(FPS)/1000

''''
TODO:
 - Implementar iterações de cálculo de física por frame nas bolas para evitar erros (entrar dentro do movePad)
 - Na criação de mapas para o jogo, botar umas letras q sinalizam cor/vida
 - Sistema de jogo:
        - Se não houver nenhuma bola, perdeu o jogo
        - Se não houver nenhum tijolo, ganhou o jogo
'''