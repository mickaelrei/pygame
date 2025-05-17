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

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Point:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = WHITE

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y
    
    def to_rect(self):
        return Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def collidepoint(self, point: Point):
        return (self.x <= point.x <= self.x + self.w and
                self.y <= point.y <= self.y + self.h)
    
    def colliderect(self, rect: Rect):
        return (self.x < rect.x + rect.w and
                self.x + self.w > rect.x and
                self.y < rect.y + rect.h and
                self.y + self.h > rect.y)

class QuadTree:
    def __init__(self, boundary: Rect, capacity: int):
        self.boundary: Rect = boundary
        self.capacity = capacity
        self.points: list[Point] = []
        self.divided = False

    def subdivide(self):
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.w, self.boundary.h
        nw = Rect(x, y, w / 2, h / 2)
        ne = Rect(x + w / 2, y, w / 2, h / 2)
        sw = Rect(x, y + h / 2, w / 2, h / 2)
        se = Rect(x + w / 2, y + h / 2, w / 2, h / 2)

        self.northwest = QuadTree(nw, self.capacity)
        self.northeast = QuadTree(ne, self.capacity)
        self.southwest = QuadTree(sw, self.capacity)
        self.southeast = QuadTree(se, self.capacity)

        # Distribute points to the new quadrants
        for point in self.points:
            if self.northwest.insert(point):
                continue
            elif self.northeast.insert(point):
                continue
            elif self.southwest.insert(point):
                continue
            elif self.southeast.insert(point):
                continue
        self.points.clear()

        self.divided = True

    def insert(self, point: Point):
        if not self.boundary.collidepoint(point):
            return False

        if not self.divided and len(self.points) < self.capacity:
            self.points.append(point)
            return True
        else:
            if not self.divided:
                self.subdivide()

            return (self.northwest.insert(point) or
                    self.northeast.insert(point) or
                    self.southwest.insert(point) or
                    self.southeast.insert(point))
        
    def query(self, range: Rect, found: list[Vector2] | None = None) -> list[Point]:
        if found is None:
            found = []
        if not self.boundary.colliderect(range):
            return found

        for point in self.points:
            if range.colliderect(point.to_rect()):
                found.append(point)

        if self.divided:
            self.northwest.query(range, found)
            self.northeast.query(range, found)
            self.southwest.query(range, found)
            self.southeast.query(range, found)

        return found
        
    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, (self.boundary.x, self.boundary.y, self.boundary.w, self.boundary.h), 1)
        if self.divided:
            self.northwest.draw(surface)
            self.northeast.draw(surface)
            self.southwest.draw(surface)
            self.southeast.draw(surface)

        for point in self.points:
            point.draw(surface)

numPoints = 500
q = QuadTree(Rect(0, 0, WIDTH, HEIGHT), 4)
for _ in range(numPoints):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    q.insert(Point(x, y, random.randint(2, 10)))

coll = False
while True:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                coll = not coll

    WINDOW.fill(BLACK)

    q.draw(WINDOW)

    if coll:
        # Find point closest to mouse position
        closest_point = None
        closest_distance = 1e10
        for point in q.query(Rect(0, 0, WIDTH, HEIGHT)):
            distance = ((point.x - mouse_pos[0]) ** 2 + (point.y - mouse_pos[1]) ** 2) ** 0.5
            if distance < point.radius and distance < closest_distance:
                closest_distance = distance
                closest_point = point

        if closest_point:
            # Query quadtree for the closest point
            radius = closest_point.radius
            found = q.query(Rect(closest_point.x - radius, closest_point.y - radius, radius * 2, radius * 2))
            print(f"Collisions: {len(found) - 1} ({(len(found) - 1)/numPoints*100:.2f}%)")

            # Draw query bounding box
            pygame.draw.rect(WINDOW, (0, 255, 0), (closest_point.x - radius, closest_point.y - radius, radius * 2, radius * 2), 1)
            for point in found:
                if point != closest_point:
                    pygame.draw.circle(WINDOW, (255, 0, 0), (int(point.x), int(point.y)), 3)
                    pygame.draw.line(WINDOW, (255, 0, 0), (int(mouse_pos[0]), int(mouse_pos[1])), (int(point.x), int(point.y)), 1)
    else:
        # Draw query from mouse pos
        size = 150
        pygame.draw.rect(WINDOW, (0, 255, 0), (mouse_pos[0] - size / 2, mouse_pos[1] - size / 2, size, size), 1)
        found = q.query(Rect(mouse_pos[0] - size / 2, mouse_pos[1] - size / 2, size, size))
        print(f"Found {len(found)} points; {len(found)/numPoints*100:.2f}% of points")

        # Draw points in the query
        for point in found:
            pygame.draw.circle(WINDOW, (0, 255, 0), (int(point.x), int(point.y)), point.radius)

    pygame.display.update()

    CLOCK.tick(60)