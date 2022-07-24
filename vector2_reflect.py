import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from math import sin, cos, radians, degrees, atan2
from random import randint

pygame.init()
WIDTH = 600
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

def clamp(n: float, minVal: float, maxVal: float) -> float:
    return min(maxVal, max(minVal, n))

class Ball:
    def __init__(self, pos: Vector2, vel: Vector2, speed=1, radius=15) -> None:
        self.pos: Vector2 = pos
        self.vel: Vector2 = vel
        self.speed = speed
        self.radius = radius

    def update(self):
        self.pos += self.vel.normalize() * self.speed
        self.pos.x = clamp(self.pos.x, self.radius + 1, WIDTH - self.radius -1)
        self.pos.y = clamp(self.pos.y, self.radius + 1, HEIGHT - self.radius -1)

    def draw(self):
        pygame.draw.circle(window, RED, (self.pos.x, self.pos.y), self.radius)
        pygame.draw.line(window, BLACK, (self.pos.x, self.pos.y), (self.pos.x + self.vel.x * self.radius, self.pos.y + self.vel.y * self.radius), 2)

class Brick:
    def __init__(self, pos, w, h) -> None:
        self.pos = pos
        self.w = w
        self.h = h
        self.angle = 0

    def draw(self):
        pygame.draw.rect(window, BLACK, (self.pos.x - self.w/2, self.pos.y - self.h/2, self.w, self.h), 0)

class Line:
    def __init__(self, start: Vector2, end: Vector2, width=2) -> None:
        self.a: Vector2 = start
        self.b: Vector2 = end
        self.width = width

    def draw(self):
        pygame.draw.line(window, BLACK, (self.a.x, self.a.y), (self.b.x, self.b.y), self.width)
        pygame.draw.circle(window, GREEN, (self.a.x, self.a.y), 5)
        pygame.draw.circle(window, RED, (self.b.x, self.b.y), 5)

ball = Ball(Vector2(WIDTH/2 - 100, 250), Vector2(1, -1))
line = Line(Vector2(300, randint(400, 550)), Vector2(550, randint(100, 250)))

lastReflect = ""
point = None
while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key in (K_a, K_LEFT):
                ball.vel.reflect_ip(Vector2(-1, 0))
            elif event.key in (K_d, K_RIGHT):
                ball.vel.reflect_ip(Vector2(1, 0))
            elif event.key in (K_w, K_UP):
                ball.vel.reflect_ip(Vector2(0, -1))
            elif event.key in (K_s, K_DOWN):
                ball.vel.reflect_ip(Vector2(0, 1))
            elif event.key == K_SPACE:
                # Reflect on line
                # Normal
                dir = (line.b - line.a).normalize()
                dist = line.a.distance_to(line.b)
                reflectLeft = Vector2(-dir.y, dir.x).normalize()
                reflectRight = Vector2(dir.y, -dir.x).normalize()

                chosen = reflectRight
                ball.vel.reflect_ip(chosen)
                print(dir)
                #point = Line(line.b + dir*(dist/2), line.b + dir*(dist/2) + chosen * 50)
                point = Line(line.b, line.b + chosen * 50)
                print(point.a)
                pass

    window.fill(WHITE)

    if point:
        point.draw()
    #pygame.draw.line(window, BLACK, (line.a.x, line.a.y), (point.b.x, point.b.y))

    ball.update()
    ball.draw()
    line.draw()

    pygame.display.update()
    clock.tick(FPS)