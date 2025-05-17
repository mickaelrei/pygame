from __future__ import annotations
import pygame
import sys
import random
from pygame.math import Vector2

pygame.init()

WIDTH = 600
HEIGHT = 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def lerp(a, b, t):
    return a + (b - a) * t

class Quad:
    def __init__(self, center: Vector2, points: list[Vector2], color=WHITE):
        """
        Initializes an instance with a center point, a list of points relative to center, and an optional color.

        The points must be provided in the following order:
         - Top left
         - Top right
         - Bottom right
         - Bottom left

        If the points are not provided in this order, the quad will be drawn/split incorrectly
        """

        self.pos = center
        self.__points = points
        self.color = color
        self.vel = Vector2(0, 0)
        self.static = False

    @staticmethod
    def fromAbsolutePoints(center, points, color=WHITE):
        return Quad(center, [p - center for p in points], color)
    
    @staticmethod
    def fromRelativePoints(center, points, color=WHITE):
        return Quad(center, points, color)
    
    def update(self, acc: Vector2, dt: float):
        if self.static: return

        self.vel += acc * dt
        self.pos += self.vel * dt

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, [self.pos + p for p in self.__points], 0 if fill else 1)
        # pygame.draw.circle(surface, self.color, self.center, 5)

    def split(self) -> list[Quad]:
        # Find the longest axis
        distX0 = self.__points[0].distance_squared_to(self.__points[1])
        distX1 = self.__points[2].distance_squared_to(self.__points[3])
        distY0 = self.__points[0].distance_squared_to(self.__points[3])
        distY1 = self.__points[1].distance_squared_to(self.__points[2])

        distX = (distX0 + distX1) / 2
        distY = (distY0 + distY1) / 2

        if distX > distY:
            # Longest on the X axis; split vertically
            return self.splitVertical()
        else:
            # Longest on the Y axis; split horizontally
            return self.splitHorizontal()

    def splitVertical(self) -> list[Quad]:
        # Random alpha between 0 and 1 to find point in top and bottom sides
        t0 = random.random()
        t1 = random.random()

        topPoint = lerp(self.__points[0], self.__points[1], t0)
        bottomPoint = lerp(self.__points[3], self.__points[2], t1)

        # Breaking on two opposite sides will generate two new quads
        # The first quad will be the left half of the original quad
        leftPoints = [
            self.__points[0].copy(),
            topPoint.copy(),
            bottomPoint.copy(),
            self.__points[3].copy(),
        ]

        # Transform it to global space
        for i in range(len(leftPoints)):
            leftPoints[i] += self.pos

        # The second quad will be the right half of the original quad
        rightPoints = [
            topPoint.copy(),
            self.__points[1].copy(),
            self.__points[2].copy(),
            bottomPoint.copy(),
        ]
        # Transform it to global space
        for i in range(len(rightPoints)):
            rightPoints[i] += self.pos

        # Calculate the center of the new quads
        centerLeftQuad = Vector2(0, 0)
        for p in leftPoints:
            centerLeftQuad += p
        centerLeftQuad /= len(leftPoints)
        centerRightQuad = Vector2(0, 0)
        for p in rightPoints:
            centerRightQuad += p
        centerRightQuad /= len(rightPoints)

        # Create the new quads
        leftQuad = Quad.fromAbsolutePoints(
            centerLeftQuad,
            leftPoints,
            self.color if not newColor else (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        )
        leftQuad.vel = self.vel.copy()
        rightQuad = Quad.fromAbsolutePoints(
            centerRightQuad,
            rightPoints,
            self.color if not newColor else (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        )
        rightQuad.vel = self.vel.copy()

        # Return the new quads
        return [leftQuad, rightQuad]

    def splitHorizontal(self) -> list[Quad]:
        # Random alpha between 0 and 1 to find point in left and right sides
        t0 = random.random()
        t1 = random.random()

        leftPoint = lerp(self.__points[0], self.__points[3], t0)
        rightPoint = lerp(self.__points[1], self.__points[2], t1)

        # Breaking on two opposite sides will generate two new quads
        # The first quad will be the top half of the original quad
        topPoints = [
            self.__points[0].copy(),
            self.__points[1].copy(),
            rightPoint.copy(),
            leftPoint.copy(),
        ]

        # Transform it to global space
        for i in range(len(topPoints)):
            topPoints[i] += self.pos

        # The second quad will be the bottom half of the original quad
        bottomPoints = [
            leftPoint.copy(),
            rightPoint.copy(),
            self.__points[2].copy(),
            self.__points[3].copy()
        ]
        # Transform it to global space
        for i in range(len(bottomPoints)):
            bottomPoints[i] += self.pos

        # Calculate the center of the new quads
        centerTopQuad = Vector2(0, 0)
        for p in topPoints:
            centerTopQuad += p
        centerTopQuad /= len(topPoints)
        centerBottomQuad = Vector2(0, 0)
        for p in bottomPoints:
            centerBottomQuad += p
        centerBottomQuad /= len(bottomPoints)

        # Create the new quads
        topQuad = Quad.fromAbsolutePoints(
            centerTopQuad,
            topPoints,
            self.color if not newColor else (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        )
        topQuad.vel = self.vel.copy()
        bottomQuad = Quad.fromAbsolutePoints(
            centerBottomQuad,
            bottomPoints,
            self.color if not newColor else (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))    
        )
        bottomQuad.vel = self.vel.copy()

        # Return the new quads
        return [topQuad, bottomQuad]

center = Vector2(WIDTH // 2, HEIGHT // 2)
size = Vector2(200, 200)
newColor = False
fill = False
initialColor = WHITE
quads: list[Quad] = []

# Start with a quad centered in the middle of the screen
quads.append(Quad.fromRelativePoints(center, [
    Vector2(-size.x / 2, -size.y / 2),
    Vector2(size.x / 2, -size.y / 2),
    Vector2(size.x / 2, size.y / 2),
    Vector2(-size.x / 2, size.y / 2)
], initialColor))
quads[0].static = True

def breakQuad():
    global lastHorizontal

    # Break the first quad in the list
    if lastHorizontal:
        newQuads = quads[0].splitVertical()
    else:
        newQuads = quads[0].splitHorizontal()
    lastHorizontal = not lastHorizontal

    # Add upwards force to the new quads
    for q in newQuads:
        diffX = q.pos.x - center.x
        if diffX < 0:
            sign = -1
        else:
            sign = 1
        q.vel += Vector2(sign * (0.2 + random.random()) * 20, -(0.3 + random.random()) * 45) * 0.9

    quads.pop(0)
    quads.extend(newQuads)

updating = False
lastHorizontal = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                for i in range(50):
                    breakQuad()
            elif event.key == pygame.K_e:
                updating = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_e:
                updating = False

    WINDOW.fill(BLACK)

    breakQuad()

    for q in quads:
        if updating:
            q.update(Vector2(0, 196), 1 / 60)
        q.draw(WINDOW)
    
    pygame.display.set_caption(f"Quad Break | {CLOCK.get_fps():.0f} FPS")
    pygame.display.update()
    CLOCK.tick(FPS)