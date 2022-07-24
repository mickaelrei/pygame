import pygame
from pygame.locals import *
import sys
from math import sin, cos, radians

pygame.init()
WIDTH = 600
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
PINK = (255, 127, 127)
PURPLE = (204, 51, 204)
CYAN = (127, 127, 255)

raio = 150
angulo = 45

def f(x):
    return 0

def drawEllipse(centerX: float, centerY: float, width: float, height: float, color: tuple[int]=BLACK, window: pygame.Surface=window, precision: int=3):
    for i in range(360*precision):
        x = centerX + cos(radians(i / precision)) * width
        y = centerY + sin(radians(i / precision)) * height

        pygame.draw.circle(window, color, (x, y), 2)

frame = 0
precisao = 3

w = 150
h = 100

orig = pygame.Vector2(w, h)
while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    window.fill(WHITE)

    drawEllipse(WIDTH//2, HEIGHT//2, w, h)

    w = orig.x + cos(radians(frame*3)) * 50
    h = orig.y + sin(radians(frame*3)) * -50

    pygame.display.update()
    frame += 1
    clock.tick(FPS)
