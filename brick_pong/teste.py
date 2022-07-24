import pygame
from pygame.locals import *
import sys
import os.path
from pygame.math import Vector2
import math
from random import randint, choices
import time

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

pathFile = os.path.dirname(__file__)

while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    window.fill(RED)

    twtSprite = pygame.image.load(os.path.join(pathFile, "images/twt.png")).convert_alpha()
    twtSprite = pygame.transform.scale(twtSprite, (mouseX, mouseY))

    window.blit(twtSprite, (0, 0))

    pygame.display.update()
    clock.tick(FPS)