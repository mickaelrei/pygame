import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from random import randint
from math import cos, sin, radians, inf

pygame.init()
WIDTH = 600
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 6000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 127, 0)

class Point:
    def __init__(self, angle: float=0, r: float=1, center: Vector2=None) -> None:
        self.angle = angle
        self.r = r
        self.center = center

def map(n, start1, stop1, start2, stop2):
    return (n - start1) / (stop1 - start1) * (stop2 - start2) + start2

def pointInPolygon(point: Vector2, vertices: list[Vector2]) -> bool:
    c = 0
    p1 = vertices[0]
    n = len(vertices)

    for i in range(1, len(vertices)):
        p2 = vertices[i % n]
        if (point.x > min(p1.x, p2.x) and
            point.x <= max(p1.x, p2.x) and
            point.y <= max(p1.y, p2.y) and
            p1.x != p2.x):
                xinters = (point.x - p1.x) * (p2.y - p1.y) / (p2.x - p1.x) + p1.y
                if (p1.y == p2.y or point.y <= xinters):
                    c += 1
        p1 = p2
    # if the number of edges we passed through is even, then it's not in the poly.
    return c % 2 != 0

# Function to draw a perfect shape with n sides, based on the given radius and center
def getVerticesForShape(sides: int=3, radius: float=50, center: Vector2=None, thickness: int=1) -> list[Vector2]:
    center = center or Vector2(WIDTH/2, HEIGHT/2)
    
    # Start with the first point
    startingAngle = -90
    if sides % 2 == 0:
        print("Going more left")
        startingAngle -= 360 / (2 * sides)

    # Keep track of all the vertices
    vertices = []

    x = center.x + cos(radians(startingAngle)) * radius
    y = center.x + sin(radians(startingAngle)) * radius
    lastPoint = Vector2(x, y)
    firstPoint = lastPoint

    for i in range(sides):
        # Get a new point
        #angle = map(i, 0, sides-1, startingAngle, 360-startingAngle)
        angle = i/sides * 360
        x = center.x + cos(radians(angle + startingAngle)) * radius
        y = center.x + sin(radians(angle + startingAngle)) * radius

        # Set the last point to be the new point and add it to the vertices list
        lastPoint = Vector2(x, y)
        vertices.append(lastPoint)
    
    # The polygon needs to end where it began
    vertices.append(firstPoint)

    # Return the vertices list
    return vertices

# Function to test the area of a shape
def testShapeArea(vertices: list[Vector2], step: int=6, surface: pygame.Surface=window):
    # Set a start and an end to the x iteration (so it doesnt cover useless parts of the screen)
    leftmost, rightmost = WIDTH, 0
    upmost, downmost = HEIGHT, 0
    for vertex in vertices:
        if vertex.x > rightmost:
            rightmost = vertex.x
        if vertex.x < leftmost:
            leftmost = vertex.x
        
        if vertex.y > downmost:
            downmost = vertex.y
        if vertex.y < upmost:
            upmost = vertex.y

    for x in range(leftmost-10, rightmost+10, step):
        for y in range(upmost-10, downmost+10, step):
            pos = Vector2(x, y)
            pygame.draw.circle(surface, GREEN if pointInPolygon(pos, vertices) else RED, pos, 3)

# Function to draw a polygon with the given vertices
def drawPolygon(vertices: list[Vector2], color: tuple=BLACK, surface: pygame.Surface=window, lineWidth: int=2):
    for i in range(len(vertices)-1):
        vertex0, vertex1 = vertices[i], vertices[i+1]
        pygame.draw.line(surface, color, vertex0, vertex1, lineWidth)

def getVerticesForPolygon(center: Vector2, points: list[Point|float]):
    # Start with the first point
    startingAngle = -90
    if sides % 2 == 0:
        print("Going more left")
        startingAngle -= 360 / (2 * sides)

    # Keep track of all the vertices
    vertices = []

    x = center.x + cos(radians((points[0].angle if type(points[0]) == Point else points[0]) - 90)) * (points[0].r if type(points[0]) == Point else radius)
    y = center.x + sin(radians((points[0].angle if type(points[0]) == Point else points[0]) - 90)) * (points[0].r if type(points[0]) == Point else radius)
    lastPoint = Vector2(x, y)
    firstPoint = lastPoint

    for point in points:
        # Get a new point
        if type(point) == Point:
            x = (point.center or center).x + cos(radians(point.angle - 90)) * point.r
            y = (point.center or center).x + sin(radians(point.angle - 90)) * point.r
        else:
            x = center.x + cos(radians(point - 90)) * radius
            y = center.y + sin(radians(point - 90)) * radius

        # Set the last point to be the new point and add it to the vertices list
        lastPoint = Vector2(x, y)
        vertices.append(lastPoint)
    
    # The polygon needs to end where it began
    vertices.append(firstPoint)

    # Return the vertices list
    return vertices

# Constants
center = Vector2(WIDTH/2, HEIGHT/2)

# Variables
radius = 250
sides = 3
alwaysNewVertex = 0
needsToBeInsideShape = 1
pointSize = 1
calcsPerFrame = 10000

points: list[Vector2] = []
lastVertex = None

# Draw the shape
starPoints = [
    Point(0, radius),
    Point(2/5*360, radius),
    Point(4/5*360, radius),
    Point(1/5*360, radius),
    Point(3/5*360, radius),
]
angle = 15
size = 6
plusPoints = [
    Point(angle, radius),
    Point(45, angle*size),
    Point(90 - angle, radius),
    Point(90 + angle, radius),
    Point(135, angle*size),
    Point(180 - angle, radius),
    Point(180 + angle, radius),
    Point(225, angle*size),
    Point(270 - angle, radius),
    Point(270 + angle, radius),
    Point(315, angle*size),
    Point(-angle, radius),
]
diamondPoints = [
    40,
    80,
    180,
    -80,
    -40
]

randomPoints = []
for i in range(15):
    randomPoints.append(randint(1, 359))

chosenShape = starPoints
# vertices = getVerticesForPolygon(Vector2(WIDTH/2, HEIGHT/2), chosenShape)
vertices = getVerticesForShape(sides, radius, center, 2)

# Set the initial point
lastPoint = center + Vector2(randint(-radius, radius), randint(-radius, radius))
while not pointInPolygon(lastPoint, vertices):
    lastPoint = center + Vector2(randint(-radius, radius), randint(-radius, radius))

while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN and event.key == K_e:
            print("oi")

    window.fill(WHITE)

    for i in range(calcsPerFrame):
        # Pick a random vertex
        newVertex = vertices[randint(0, len(vertices)-1)]
        if alwaysNewVertex:
            while newVertex == lastVertex:
                newVertex = vertices[randint(0, len(vertices)-1)]
            
            lastVertex = newVertex
        
        # Create a new point in the middle of the last point and the chosen vertex
        newPoint = lastPoint.lerp(newVertex, .5)
        # Make the last point be the new point
        lastPoint = newPoint

        # Add the new point to the points list
        if needsToBeInsideShape and not pointInPolygon(newPoint, vertices):
            continue

        points.append(newPoint)

    
    # Draw the polygon's vertices
    for i in range(len(vertices)-1):
        pygame.draw.line(window, BLACK, vertices[i], vertices[i+1], 2)

    # Draw all points
    for point in points:
        pygame.draw.circle(window, BLACK, point, pointSize)

    pygame.display.set_caption(f"Chaos Game | FPS: {clock.get_fps():.0f}")
    pygame.display.update()
    clock.tick(FPS)
