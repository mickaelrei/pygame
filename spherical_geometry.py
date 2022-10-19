from random import randint
import pygame
from pygame.locals import *
import sys
from math import sin, cos, pi
from pygame.math import Vector3

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

latStep = 100
lonStep = 100
r = 350
center = Vector3(WIDTH/2, HEIGHT/2, 0)
frame = 0
frameStep = 150

def map(n, start1, stop1, start2, stop2):
    return (n - start1) / (stop1 - start1) * (stop2 - start2) + start2

while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    window.fill(WHITE)

    for i in range(latStep):
        lat = map(i, 0, latStep-1, 0, 2*pi)
        for j in range(lonStep):
            lon = map(j, 0, lonStep-1, 0, pi)

            x = center.x + r * sin(lon + frame/frameStep) * cos(lat + frame/frameStep)
            y = center.y + r * sin(lon + frame/frameStep) * sin(lat + frame/frameStep)
            z = center.z + r * cos(lon + frame/frameStep)

            pygame.draw.circle(window, (randint(0, 255), randint(0, 255), randint(0, 255)), (x, y), 3)

    pygame.display.update()
    frame += 1
    clock.tick(FPS)