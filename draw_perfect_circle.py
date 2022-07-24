import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from math import sin, cos, radians, degrees, atan2
from random import randint

pygame.init()
WIDTH = 800
HEIGHT = 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 6000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

def map(n, start1, stop1, start2, stop2):
    return (n - start1) / (stop1 - start1) * (stop2 - start2) + start2

def clamp(n, minVal, maxVal):
    if n < minVal:
        return minVal
    elif n > maxVal:
        return maxVal
    return n

CENTER = Vector2(WIDTH/2, HEIGHT/2)
firstClickPos = None
showHelp = True
radius = None
points = []

while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            try:
                firstClickPos = mousePos
                radius = (firstClickPos - CENTER).magnitude()
            except ValueError:
                firstClickPos = None
                continue
        elif event.type == MOUSEBUTTONUP:
            firstClickPos = None
            radius = None
            points = []

    window.fill(WHITE)

    if firstClickPos:
        if showHelp:
            # Draw a circle to show where the user should draw
            pygame.draw.circle(window, (150, 150, 150), (CENTER.x, CENTER.y), radius, 2)

        # Check radius difference
        currentRadius = None
        try:
            currentRadius = (mousePos - CENTER).magnitude()
        except ValueError:
            firstClickPos = None
            radius = None
            continue

        if not currentRadius: continue

        color = pygame.Color(0, 0, 0)
        print(f"Dist from Center: {radius:.2f}, radius diff: {abs(currentRadius - radius):.2f}")
        color.hsla = (clamp(map(abs(currentRadius - radius), 0, radius/7, 90, 0), 0, 90) % 360, 100, 50, 0)
        #print(f"{color.hsla[0]:.2f}, {abs(currentRadius - radius):.2f}, {max(WIDTH, HEIGHT)/2 - radius:.2f}")
        points.append([mousePos, color])

    for i in range(len(points)-1):
        idx1 = points[i]
        idx2 = points[i+1]
        pygame.draw.line(window, idx1[1], (idx1[0].x, idx1[0].y), (idx2[0].x, idx2[0].y), 7)

    # Draw the middle point
    pygame.draw.circle(window, BLACK, (CENTER.x, CENTER.y), 15)

    pygame.display.update()
    clock.tick(FPS)