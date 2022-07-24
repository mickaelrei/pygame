import pygame
from pygame.locals import *
import sys
from math import sin, cos, radians, pi, floor
from random import randint

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

class Blob:
    def __init__(self, r: int=150, numPoints: int=50, center: pygame.Vector2=None, color: tuple=BLACK) -> None:
        self.r = r
        self.numPoints = numPoints
        self.center = center or pygame.Vector2(WIDTH/2, HEIGHT/2)
        self.color = color
        self.m = 1
        self.speed = 1

    def draw(self, surface=window):
        points = []
        for i in range(self.numPoints+1):
            a = i/self.numPoints * 2 * pi
            r = self.r + sin(a * self.m + frame * self.speed) * 15

            x = self.center.x + r * cos(a)
            y = self.center.y + r * sin(a)
            points.append((x, y))

        pygame.draw.polygon(surface, self.color, points)

frame = 0
b = Blob(numPoints=1000)
minM = 1
maxM = 50
minSpeed = 1/15
maxSpeed = 5

while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    window.fill(WHITE)

    b.m = floor(pygame.mouse.get_pos()[0] / WIDTH * (maxM - minM) + minM)
    b.speed = pygame.mouse.get_pos()[1] / WIDTH * (maxSpeed - minSpeed) + minSpeed
    b.draw()

    pygame.display.update()
    frame += 1
    clock.tick(FPS)