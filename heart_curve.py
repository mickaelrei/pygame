import pygame
from pygame.locals import *
import sys
from math import sin, cos
from random import randint

pygame.init()
WIDTH = 800
HEIGHT = 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
PINK = (255, 127, 127)
PURPLE = (204, 51, 204)
CYAN = (127, 127, 255)

alpha = 255
frame = 0
centerX = WIDTH/2
centerY = HEIGHT/2
precision = 20
clearScreen = True
radiusX = 20
radiusY = 20

drawSurface = pygame.Surface((WIDTH, HEIGHT))
drawSurface.fill(WHITE)
drawSurface.set_alpha(alpha)
window.fill(WHITE)
while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    if clearScreen:
        drawSurface.fill(WHITE)

    for i in range(360*precision):
        t = i/precision
        offset = i * .1
        
        x = centerX + (16 * sin(t)**3) * abs(sin(frame / 30)**3) * radiusX
        y = centerY - (13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t)) * abs(sin(frame / 30)**3) * radiusY

        color = pygame.Color(0, 0, 0)
        color.hsla = ((frame * 15 + t * 58) % 360, 100, 50, alpha % 100)
        pygame.draw.circle(drawSurface, color, (x, y), 15)

    if clearScreen:
        window.fill(WHITE)    

    window.blit(drawSurface, (0, 0))

    alpha = abs(sin(frame/45)) * 255

    pygame.display.set_caption(f"FPS: {clock.get_fps():.0f}")
    pygame.display.update()
    frame += 1
    clock.tick(FPS)