import pygame
from pygame.locals import *
import sys
from math import sin, cos, pi
from random import randint
from pygame.math import Vector2

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

r1 = randint(144, 160)
r2 = randint(144, 160)
m1 = randint(39, 41)
m2 = randint(39, 41)
a1 = pi + pi/10
a2 = 0
a1_v = -.1
a2_v = .01

g = 1
maxSinCos = 1e6
calcsPerFrame = 1
startPos = Vector2(WIDTH/2, HEIGHT/2)
points: list[tuple[float, float]] = []

frame = 0
while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_f:
                print(len(points))

    for _ in range(calcsPerFrame):
        # Arm 1
        num1 = -g * (2 * m1 + m2) * sin(a1 % maxSinCos)
        num2 = -m2 * g * sin((a1 - 2 * a2) % maxSinCos)
        num3 = -2 * sin((a1 - a2) % maxSinCos) * m2
        num4 = a2_v * a2_v * r2 + a1_v * a1_v * r1 * cos((a1 - a2) % maxSinCos)
        den = r1 * (2 * m1 + m2 - m2 * cos((2 * a1 - 2 * a2) % maxSinCos))
        a1_a = (num1 + num2 + num3 * num4) / den

        # Arm 2
        num1 = 2 * sin((a1 - a2) % maxSinCos)
        num2 = (a1_v * a1_v * r1 * (m1 + m2))
        num3 = g * (m1 + m2) * cos(a1 % maxSinCos)
        num4 = a2_v * a2_v * r2 * m2 * cos((a1 - a2) % maxSinCos)
        den = r2 * (2 * m1 + m2 - m2 * cos((2 * a1 - 2 * a2) % maxSinCos))
        a2_a = (num1 * (num2 + num3 + num4)) / den

        # Add velocity and angle
        a1_v += a1_a
        a2_v += a2_a
        a1 += a1_v
        a2 += a2_v

        # Calculate positions
        x1 = startPos.x + r1 * sin(a1)
        y1 = startPos.y + r1 * cos(a1)
        x2 = x1 + r2 * sin(a2)
        y2 = y1 + r2 * cos(a2)

        points.append((x2, y2))

    # Draw cocks
    window.fill(WHITE)

    if len(points) >= 2:
        pygame.draw.lines(window, RED, False, points, round(abs(sin(frame/25))*40))

    # Draw lines and points
    pygame.draw.line(window, BLACK, (startPos.x, startPos.y), (x1, y1), 3)
    pygame.draw.line(window, BLACK, (x1, y1), (x2, y2), 3)
    pygame.draw.circle(window, CYAN, (x2, y2), m2 / 2)
    pygame.draw.circle(window, CYAN, (x1, y1), m1 / 2)

    pygame.display.update()
    frame += 1
    clock.tick(FPS)