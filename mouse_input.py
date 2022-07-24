import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from math import pi
from random import randint

pygame.init()
WIDTH = 400
HEIGHT = 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
PINK = (255, 127, 127)
PURPLE = (204, 51, 204)
CYAN = (127, 127, 255)

while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    buttons = pygame.mouse.get_pressed(5)
    print(" ".join([str(x) for x in buttons]))

    window.fill(WHITE)

    pygame.display.update()
    clock.tick(FPS)