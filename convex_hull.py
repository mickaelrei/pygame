import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from math import inf, cos, pi, radians, sin, atan, atan2
from random import randint, random
from time import time

pygame.init()
WIDTH = 600
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (127, 0, 255)
YELLOW = (255, 0, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (127, 0, 255)
COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

def convertAngle(angle: float) -> float:
    # If negative, make it positive
    if angle < 0:
        return angle + 360
    
    # Positive, just return the angle
    return angle

    # -180 -> 180
    # -135 -> 225
    # -90  -> 270
    # -45  -> 315

def vectorAngle(p1: Vector2, p2: Vector2) -> float:
    if p1 == p2:
        print("Same point")
        return 0
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    dir = (p2 - p1).normalize()

    # ang = atan(dy / dx)
    ang = atan2(dir.y, dir.x)
    return ang * 180 / pi

debug = 0
def getConvexHull(points: list[Vector2]) -> list[Vector2]:
    convexHull: list[Vector2] = []

    # Get the first point
    leftmost: Vector2 = None
    for point in points:
        if leftmost is None:
            leftmost = point
            continue
        
        if point.x < leftmost.x:
            leftmost = point

    convexHull.append(leftmost)

    # Get other points
    lastPoint = convexHull[0]
    lastAngle = -90
    while True:# and convexHull[0] != convexHull[-1]:
        smallestAngle = 360 + lastAngle
        nextPoint = None
        angles = []
        for point in points:
            # if convexHull.count(point) > 0: continue
            if point == lastPoint: continue

            if debug:
                clearWindow()
                drawPoints()
                pygame.draw.line(window, RED, lastPoint, point, 2)
                if nextPoint:
                    pygame.draw.line(window, GREEN, lastPoint, nextPoint, 2)
                endX = point.x + cos(lastAngle)
                # pygame.draw.line(window, PURPLE, point, )
                if len(convexHull) >= 2:
                    pygame.draw.lines(window, BLUE, False, convexHull)
                render()

            angle = vectorAngle(lastPoint, point)
            if lastAngle > 0:
                angle = convertAngle(angle)
            angles.append(angle)
            if debug:
                print(f"Last: {lastAngle:.2f}, Current: {angle:.2f}, Smallest: {smallestAngle:.2f}, Req: > {lastAngle}")
                while True:
                    if getInput(): break
            
            # Check if valid next hull point
            if angle <= smallestAngle and angle > lastAngle:
                # If it's the same exact angle, get the farthest
                if angle == smallestAngle and nextPoint:
                    if lastPoint.distance_squared_to(point) > lastPoint.distance_squared_to(nextPoint):
                        smallestAngle = angle
                        nextPoint = point
                else:
                    smallestAngle = angle
                    nextPoint = point
            # elif angle == smallestAngle:
            #     print("SAME EXACT ANGLE")
            #     pygame.draw.circle(window, GREEN, lastPoint, 4)
            #     pygame.draw.circle(window, GREEN, point, 4)

        if nextPoint is None:
            print(f"No next point. LastAngle: {lastAngle}, SmallestAngle: {smallestAngle}, Angles:\n{angles}, MinMax: ({min(angles)}, {max(angles)})")

            break

        convexHull.append(nextPoint)
        lastPoint = nextPoint
        lastAngle = smallestAngle

        # Check if hull is closed
        if nextPoint == convexHull[0]:
            break

    return convexHull
    # smallestAngle = 360
    # nextPoint: Vector2 = None
    # for point in points:
    #     # If it's in the convex hull, skip it
    #     if convexHull.count(point) > 0: continue

    #     if point == leftmost: continue

    #     # Check if angle is smaller
    #     angle = vectorAngle(leftmost, point)
    #     if angle < smallestAngle and angle > -90:
    #         smallestAngle = angle
    #         nextPoint = point

    #     # if nextPoint == convexHull[0]:
    #     #     break

    # convexHull.append(nextPoint)

    # smallestAngle2 = 360
    # nextPoint1: Vector2 = None
    # for point in points:
    #     # If it's in the convex hull, skip it
    #     if convexHull.count(point) > 0: continue

    #     # Check if angle is smaller
    #     angle = vectorAngle(nextPoint, point)
    #     if angle < smallestAngle2 and angle > -90 + smallestAngle:
    #         # print(angle)
    #         smallestAngle2 = angle
    #         nextPoint1 = point

    # # print(smallestAngle)

    # r = 2
    # pygame.draw.circle(window, RED, leftmost, r)
    # pygame.draw.circle(window, GREEN, nextPoint, r)
    # pygame.draw.circle(window, BLUE, nextPoint1, r)

def clearWindow():
    window.fill(BLACK)

def getInput():
    global da
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_f:
                return True

    return False

def generatePoints(n: int, border: int) -> list[Vector2]:
    points: list[Vector2] = []
    for i in range(n):
        while True:
            x = randint(border, WIDTH - border)
            y = randint(border, HEIGHT - border)
            for point in points:
                if point.x == x and point.y == y:
                    continue

            break

        points.append(Vector2(x, y))

    return points

def drawPoints():
    for point in points:
        pygame.draw.circle(window, WHITE, point, 2)

def render():
    pygame.display.update()
    clock.tick(FPS)


numPoints = 100
border = 50
points = generatePoints(numPoints, border)

a = 0
da = 0
while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in (K_LEFT, K_a):
                da += .01
            elif event.key in (K_RIGHT, K_d):
                da += -.01
            elif event.key == K_e:
                points = generatePoints(numPoints, border)
        elif event.type == KEYUP:
            if event.key in (K_LEFT, K_a):
                da += -.01
            elif event.key in (K_RIGHT, K_d):
                da += .01
    
    window.fill(BLACK)

    hull = getConvexHull(points)
    drawPoints()
    # print(hull)
    # print(len(hull))
    for i in range(len(hull)-1):
        p1 = hull[i]
        p2 = hull[i+1]
        pygame.draw.line(window, COLORS[i%len(COLORS)], p1, p2, 1)

    render()