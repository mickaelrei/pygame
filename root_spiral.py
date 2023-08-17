import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from math import inf, cos, pi, radians, sin, atan, atan2
from random import randint, random
from time import time

pygame.init()
WIDTH = 800
HEIGHT = 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 6000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 127, 0)
YELLOW = (255, 0, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (127, 0, 255)
COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

def drawText(text: str, pos: Vector2, fontSize: int=18, fontType: str="comicsans", bold: bool=False,
             italic: bool=False, antiAlias: bool=False, textColor: tuple=BLACK, bgColor: tuple=None,
             centerX: float=0, centerY: float=0, surface: pygame.Surface=window):
    font = pygame.font.SysFont(fontType, fontSize, bold, italic)
    textSurface = font.render(text, antiAlias, textColor, bgColor)
    textRect = textSurface.get_rect()
    surface.blit(textSurface, [pos.x + (textRect.width/2) * centerX, pos.y + (textRect.height/2) * centerY])

def drawPoints():
    global n, angle, rangeMult, lastPoint, lineWidth
    
    # Get coords
    for i in range(1):
        root = n**.5

        x = center.x + cos(radians(angle)) * root * rangeMult
        y = center.y + sin(radians(angle)) * root * rangeMult
        point = Vector2(x, y)
        
        # Draw at coord
        color = pygame.Color(0, 0, 0, 0)
        color.hsla = (angle / 360 * 255, 100, 50, 100)
        color = COLORS[n % len(COLORS)]
        pygame.draw.line(window, color, center, point, lineWidth)
        if lastPoint:
            pygame.draw.line(window, color, point, lastPoint, lineWidth)

        lastPoint = point

        perfectSquare = round(root) == root
        text = f"√{n} {perfectSquare and '=' or '≈'} {perfectSquare and int(root) or round(root, 3)}"
        if includeText:
            drawText(text, point, fontSize=17, fontType="arial", bold=True)

        # Increase variables
        n += 1
        angle = (angle + angleInc) % 360

        print(f"Difference: {n**.5 - (n-1)**.5}")

n = 1
angle = 180
angleInc = 13
rangeMult = 15
lineWidth = 3
center = Vector2(WIDTH/2, HEIGHT/2)
lastPoint = None
includeText = True

window.fill(WHITE)
while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_e:
                drawPoints()

    drawPoints()

    pygame.display.set_caption(f"Root Spiral | FPS: {clock.get_fps():.0f}")
    pygame.display.update()
    clock.tick(FPS)