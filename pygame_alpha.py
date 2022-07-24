from random import randint
import pygame
from pygame.locals import *
import sys
from math import sin, cos, pi
from pygame.math import Vector2

pygame.init()
WIDTH = 800
HEIGHT = 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
PINK = (255, 127, 127)
PURPLE = (204, 51, 204)
CYAN = (127, 127, 255)

# Create surface for drawing
drawSurface = pygame.Surface((WIDTH, HEIGHT))
drawSurface.fill(WHITE)
window.fill(WHITE)


class WeirdBall:
    def __init__(self, _circleRadius: int=None, _numCircles: int=None, _circleOffsetMult: float=None,
                _radiusX: float=None, _radiusY: float=None, _rotSlownessX: float=None,
                _rotSlownessY: float=None, _colorChangeSpeed: float=None, _colorMult: float=None,
                _center: Vector2=None, _initialRotation: int=None) -> None:
        self.circleRadius = _circleRadius or circleRadius
        self.numCircles = _numCircles or numCircles
        self.circleOffsetMult = _circleOffsetMult or circleOffsetMult
        self.radiusX = _radiusX or radiusX
        self.radiusY = _radiusY or radiusY
        self.rotSlownessX = _rotSlownessX or rotSlownessX
        self.rotSlownessY = _rotSlownessY or rotSlownessY
        self.colorChangeSpeed = _colorChangeSpeed or colorChangeSpeed
        self.colorMult = _colorMult or colorMult
        self.center = _center or Vector2(centerX, centerY)
        self.initialRotation = _initialRotation or 0
        print(self.initialRotation)

    def draw(self, surface: pygame.Surface=window) -> None:
        for i in range(self.numCircles):
            offset = i * self.circleOffsetMult
            x = self.center.x + cos(frame / self.rotSlownessX + offset) * self.radiusX
            y = self.center.y + sin(frame / self.rotSlownessY + offset) * self.radiusY
            '''x = centerX + (16 * sin(frame)**3) * radiusX
            y = centerY + (13 * cos(frame) - 5 * cos(2 * frame) - 2 * cos(3 * frame) - cos(4 * frame)) * radiusY'''

            color = pygame.Color(0, 0, 0, 0)
            color.hsla = ((frame * self.colorChangeSpeed + i * self.colorMult) % 360, 100, 50, alpha/255 * 100)

            pygame.draw.circle(surface, color, (x, y), self.circleRadius)

# Constants
centerX = WIDTH//2
centerY = HEIGHT//2

# Variables
clearScreen = True
circleRadius = 35
numCircles = 600
circleOffsetMult = .05
radiusX = 150
radiusY = 250
rotSlownessX = 45
rotSlownessY = 45
colorChangeSpeed = .0001
colorMult = 3
alphaChangeSlowness = 1500
alpha = 255

balls: list[WeirdBall] = []

numBalls = 10
for i in range(numBalls):
    ball = WeirdBall(
        _circleRadius=None,
        _numCircles=40,
        _circleOffsetMult=None,
        _radiusX=radiusX+i*10,#randint(50, 250),
        _radiusY=radiusY-i*10,#randint(50, 250),
        #_colorChangeSpeed=randint(15, 50)/10,
        #_colorMult=randint(10, 50)/10,
        _rotSlownessX=50,
        _rotSlownessY=25,
        _center=None,
        )
    balls.append(ball)

# Keep track of current frame
frame = 0
while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    if clearScreen:
        drawSurface.fill(WHITE)
    drawSurface.set_alpha(alpha)

    for ball in balls:
        ball.draw(drawSurface)

    if clearScreen:
        window.fill(WHITE)
        window.blit(drawSurface, (0, 0))

    alpha = abs(cos(frame / alphaChangeSlowness)) * 255

    pygame.display.update()
    frame += 1
    clock.tick(FPS)