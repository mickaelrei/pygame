import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
import math
from random import randint
from time import time

pygame.init()
WIDTH = 700
HEIGHT = 700
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 6000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

def f(x: float) -> float:
    return math.cos(1 / (0.6 + abs(math.sin(x)))) * x**2 * 0.1 + math.sin(x) * 0.1

def map(n, start1, stop1, start2, stop2):
    return (n - start1) / (stop1 - start1) * (stop2 - start2) + start2

def clamp(n, minVal, maxVal):
    if n < minVal:
        return minVal
    elif n > maxVal:
        return maxVal
    return n

def drawText(text: str, pos: Vector2, fontSize: int=18, fontType: str="comicsans", bold: bool=False,
             italic: bool=False, antiAlias: bool=False, textColor: tuple=BLACK, bgColor: tuple=None,
             centerX: float=0, centerY: float=0, surface: pygame.Surface=window):
    font = pygame.font.SysFont(fontType, fontSize, bold, italic)
    textSurface = font.render(text, antiAlias, textColor, bgColor)
    textRect = textSurface.get_rect()
    surface.blit(textSurface, [pos.x + (textRect.width/2) * centerX, pos.y + (textRect.height/2) * centerY])

# Graph info
pointColor = (97, 97, 225)
pointWidth = 3
axisColor = (50, 50, 50)
axisWidth = 2
numsOnAxes = 10
numsOffset = Vector2(-10, 10)
numsDecimalDigits = 2
numsAxisColor = (150, 150, 150)
numsAxisWidth = 1

# Screen graph dimension
graphDimension = 20
graphOffset = Vector2(0, 0)
graphZoomStep = .3
minDimension = .1
maxDimension = 1000

# States
mouseDown = False
drawLines = True
numPoints = 5000

while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEWHEEL:
            graphDimension = clamp(graphDimension - event.y * graphZoomStep, minDimension, maxDimension)
        elif event.type == MOUSEMOTION and mouseDown:
            graphOffset += Vector2(event.rel[0], event.rel[1])

    # Get mouse buttons state
    left, middle, right = pygame.mouse.get_pressed(3)
    mouseDown = left

    window.fill(WHITE)

    # Calculate plane offset
    planeOffset = Vector2(graphOffset.x/WIDTH * graphDimension, graphOffset.y/HEIGHT * graphDimension)

    # Draw axes
    pygame.draw.line(window, axisColor, (0, HEIGHT/2 + graphOffset.y), (WIDTH, HEIGHT/2 + graphOffset.y), axisWidth)
    pygame.draw.line(window, axisColor, (WIDTH/2 + graphOffset.x, 0), (WIDTH/2 + graphOffset.x, HEIGHT), axisWidth)

    # Draw zero on origin
    drawText("0", Vector2(WIDTH/2 + numsOffset.x + graphOffset.x, HEIGHT/2 + numsOffset.y + graphOffset.y), centerX=3, centerY=-1)

    # Grid lines on X axis
    minX = int(-graphOffset.x) // int(WIDTH / numsOnAxes)
    for i in range(minX, minX + numsOnAxes + 1):
        if i == numsOnAxes / 2: continue
        
        # Calculate number and position
        numX = round(-graphDimension / 2 + graphDimension/numsOnAxes * i, numsDecimalDigits)
        posX = map(i, 0, numsOnAxes, 0, WIDTH)

        # Draw horizontal line
        pygame.draw.line(window, numsAxisColor, (posX + graphOffset.x, 0), (posX + graphOffset.x, HEIGHT), numsAxisWidth)

        # Draw the number on axis
        drawText(str(numX), Vector2(posX + numsOffset.x + graphOffset.x, HEIGHT/2 + numsOffset.y + graphOffset.y), centerY=-1, centerX=0)
        
    # Grid lines on Y axis
    minY = int(graphOffset.y) // int(HEIGHT / numsOnAxes) + 1
    for i in range(minY, minY + numsOnAxes + 1):
        if i == numsOnAxes / 2: continue
        
        # Calculate number and position
        numY = round(-graphDimension / 2 + graphDimension/numsOnAxes * i, numsDecimalDigits)
        posY = map(i, 0, numsOnAxes, HEIGHT, 0)

        # Draw vertical line
        pygame.draw.line(window, numsAxisColor, (0, posY + graphOffset.y), (WIDTH, posY + graphOffset.y), numsAxisWidth)

        # Draw the number on axis
        drawText(str(numY), Vector2(WIDTH/2 + numsOffset.x + graphOffset.x, posY + numsOffset.y + graphOffset.y), centerY=0, centerX=1)

    # Calculate all points
    lastPoint: Vector2 | None = None
    for i in range(numPoints):
        x = map(i, 0, numPoints-1, -graphDimension * 0.5 - planeOffset.x, graphDimension * 0.5 - planeOffset.x)
        try:
            y = float(f(x))
        except:
            continue

        # New point
        point = Vector2(x, y)
        x1 = map(point.x, -graphDimension * 0.5, graphDimension * 0.5, 0, WIDTH)
        y1 = map(point.y, -graphDimension * 0.5, graphDimension * 0.5, HEIGHT, 0)

        if drawLines and lastPoint is not None:
            # Use last point to draw line
            x2 = map(lastPoint.x, -graphDimension * 0.5, graphDimension * 0.5, 0, WIDTH)
            y2 = map(lastPoint.y, -graphDimension * 0.5, graphDimension * 0.5, HEIGHT, 0)

            # HACK: Draw line only if distance is small (happens in asymptotes for example)
            if Vector2(x1, y1).distance_to(Vector2(x2, y2)) < 1e4:
                pygame.draw.line(window, pointColor, (x1 + graphOffset.x, y1 + graphOffset.y), (x2 + graphOffset.x, y2 + graphOffset.y), pointWidth)
        else:
            # Draw point
            pygame.draw.circle(window, pointColor, (x1 + graphOffset.x, y1 + graphOffset.y), pointWidth / 2)

        lastPoint = point

    pygame.display.update()
    clock.tick(FPS)