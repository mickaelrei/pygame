import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
import math
import numpy
from random import randint
from time import time

pygame.init()
WIDTH = 1300
HEIGHT = 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 6000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

def f(x: float) -> float:
    try:
        return math.sin(x)
    except ZeroDivisionError:
        return None
    except ValueError:
        return None
    except TypeError:
        return None

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
graphStartX = -100
graphEndX = 100
pointColor = (97, 97, 225)
pointWidth = 3
axisColor = (50, 50, 50)
axisWidth = 2
numsOnAxes = 5
numsOffset = Vector2(-10, 10)
numsDecimalDigits = 2
numsAxisColor = (150, 150, 150)
numsAxisWidth = 1

# Screen graph dimension
graphDimension = 10
graphOffset = Vector2(0, 0)
graphZoomStep = .3
minDimension = .1
maxDimension = 1000

# States
mouseDown = False
drawLines = True
'''screenStartX = -10
screenEndX = 10
screenStartY = -10
screenEndY = 10'''
steps = 75
numPoints = 1000

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
    planeOffset = Vector2(graphOffset.x/WIDTH * graphDimension * 2, graphOffset.y/HEIGHT * graphDimension * 2)

    # Draw axes
    pygame.draw.line(window, axisColor, (0, HEIGHT/2 + graphOffset.y), (WIDTH, HEIGHT/2 + graphOffset.y), axisWidth)
    pygame.draw.line(window, axisColor, (WIDTH/2 + graphOffset.x, 0), (WIDTH/2 + graphOffset.x, HEIGHT), axisWidth)

    # Draw number points
    # Start with the middle zero
    drawText("0", Vector2(WIDTH/2 + numsOffset.x + graphOffset.x, HEIGHT/2 + numsOffset.y + graphOffset.y), centerX=3, centerY=-1)

    # Do on X and Y axis, up and down
    for i in range(numsOnAxes):
        # Calculate numbers and positions
        # Left
        numLeft = round(-graphDimension + graphDimension/numsOnAxes * i, numsDecimalDigits) # + planeOffset.x
        xLeft = map(i, 0, numsOnAxes, 0, WIDTH/2)

        # Right
        numRight = round(graphDimension - graphDimension/numsOnAxes * i, numsDecimalDigits) # + planeOffset.x
        xRight = map(i, 0, numsOnAxes, WIDTH, WIDTH/2)

        # Up
        numUp = round(graphDimension - graphDimension/numsOnAxes * i, numsDecimalDigits) # + planeOffset.y
        yUp = map(i, 0, numsOnAxes, 0, HEIGHT/2)

        # Down
        numDown = round(-graphDimension + graphDimension/numsOnAxes * i, numsDecimalDigits) # + planeOffset.y
        yDown = map(i, 0, numsOnAxes, HEIGHT, HEIGHT/2)

        # Draw horizontal and vertical lines
        pygame.draw.line(window, numsAxisColor, (xLeft + graphOffset.x, 0), (xLeft + graphOffset.x, HEIGHT), numsAxisWidth)
        pygame.draw.line(window, numsAxisColor, (xRight + graphOffset.x, 0), (xRight + graphOffset.x, HEIGHT), numsAxisWidth)
        pygame.draw.line(window, numsAxisColor, (0, yUp + graphOffset.y), (WIDTH, yUp + graphOffset.y), numsAxisWidth)
        pygame.draw.line(window, numsAxisColor, (0, yDown + graphOffset.y), (WIDTH, yDown + graphOffset.y), numsAxisWidth)

        # Draw the numbers on axes
        drawText(str(numLeft), Vector2(xLeft + numsOffset.x + graphOffset.x, HEIGHT/2 + numsOffset.y + graphOffset.y), centerY=-1, centerX=0)
        drawText(str(numRight), Vector2(xRight + numsOffset.x + graphOffset.x, HEIGHT/2 + numsOffset.y + graphOffset.y), centerY=-1, centerX=-1)
        drawText(str(numUp), Vector2(WIDTH/2 + numsOffset.x + graphOffset.x, yUp + numsOffset.y + graphOffset.y), centerY=0, centerX=1)
        drawText(str(numDown), Vector2(WIDTH/2 + numsOffset.x + graphOffset.x, yDown + numsOffset.y + graphOffset.y), centerY=0, centerX=1)

    # Calculate all points
    points: list = []
    #for i in range(round(graphStartX*steps), round(graphEndX*steps)):
    for i in range(numPoints):
        x = map(i, 0, numPoints-1, -graphDimension - planeOffset.x, graphDimension - planeOffset.x)
        #x = i/steps
        y = f(x)
        if y is None:
            continue

        # Update highest and lowest Y
        # if y < lowestY:
        #     lowestY = y
        # if y > highestY:
        #     highestY = y

        points.append(Vector2(x, y))

    # Draw points
    for i in range(len(points)-1):
        point1 = points[i]
        point2 = points[i+1]

        x1 = map(point1.x, -graphDimension, graphDimension, 0, WIDTH)
        y1 = map(point1.y, -graphDimension, graphDimension, HEIGHT, 0)

        x2 = map(point2.x, -graphDimension, graphDimension, 0, WIDTH)
        y2 = map(point2.y, -graphDimension, graphDimension, HEIGHT, 0)

        if drawLines:
            if Vector2(x1, y1).distance_to(Vector2(x2, y2)) < 1e4:
                pygame.draw.line(window, pointColor, (x1 + graphOffset.x, y1 + graphOffset.y), (x2 + graphOffset.x, y2 + graphOffset.y), pointWidth)
        else:
            pygame.draw.circle(window, pointColor, (x1 + graphOffset.x, y1 + graphOffset.y), pointWidth)
    
    pygame.display.update()
    clock.tick(FPS)