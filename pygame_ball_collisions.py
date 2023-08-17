import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from random import randint

# Start pygame window
pygame.init()
WIDTH = 1300
HEIGHT = 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
clock = pygame.time.Clock()

# Setup colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (255, 127, 127)
PURPLE = (204, 51, 204)
CYAN = (127, 127, 255)
colors = [WHITE, RED, BLACK, PINK, PURPLE, CYAN]

# Utility functions
def clamp(x: float, minVal: float, maxVal: float) -> float:
    return min(maxVal, max(x, minVal))

def sign(x: float) -> float:
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0

def distanceSquaredTo(pos1: Vector2, pos2: Vector2) -> float:
    return (pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2

def distanceTo(pos1: Vector2, pos2: Vector2) -> float:
    return ((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2) ** .5

def checkForSelectedBall():
    global selectedBall

    for ball in balls[::-1]:
        if distanceSquaredTo(ball.pos, mousePos) < ball.radius**2:
            selectedBall = ball
            break

class Ball:
    def __init__(self, pos: Vector2, radius=25, color: tuple=BLACK, vel: Vector2=None, acc: Vector2=None, name: str=None) -> None:
        self.acc: Vector2 = acc or Vector2(0, 0)
        self.vel: Vector2 = vel or Vector2(0, 0)
        self.pos: Vector2 = pos
        self.color = color
        self.radius = radius
        self.mass = self.radius * massMultiplier
        self.name = str(name)

    def applyForce(self, force: Vector2) -> None:
        self.acc += force * self.mass

    def checkBallOverlap(self, other) -> bool:
        if isinstance(other, Ball):
            return distanceSquaredTo(self.pos, other.pos) < (self.radius + other.radius)**2

    def update(self) -> None:
        # Reduce acceleration for friction
        self.acc.x = -self.vel.x * ballDrag
        self.acc.y = -self.vel.y * ballDrag
        # Update velocity and position
        self.vel += self.acc
        if wallBorders:
            self.pos = Vector2(clamp(self.pos.x + self.vel.x, self.radius - 1, WIDTH-self.radius + 1), clamp(self.pos.y + self.vel.y, self.radius - 1, HEIGHT-self.radius + 1))
        else:
            self.pos += self.vel

        if wallBorders:
            # Check collisions with walls
            # X axis
            if (self.pos.x + self.radius > WIDTH or self.pos.x - self.radius < 0) and abs(self.vel.x) > .01:
                self.vel.x *= -1
            # Y axis
            if (self.pos.y + self.radius > HEIGHT or self.pos.y - self.radius < 0) and abs(self.vel.y) > .01:
                self.vel.y *= -1 * (1 - bounceRedution)

                # Reduce X speed based on ground friction
                self.vel.x *= (1 - groundFriction)
        elif rotateBallsAroundScreen:
            # Check if outside wall borders
            # X axis
            if self.pos.x > WIDTH:
                self.pos.x = 1
            elif self.pos.x < 0:
                self.pos.x = WIDTH - 1

            # Y axis
            if self.pos.y > HEIGHT:
                self.pos.y = 1
            elif self.pos.y < 0:
                self.pos.y = HEIGHT - 1

        # If the speed is too low, set to zero
        if self.vel.magnitude() < .01:
            self.vel.x = 0
            self.vel.y = 0

    def __repr__(self) -> str:
        return self.name

    def draw(self, surface: pygame.Surface=window) -> None:
        pygame.draw.circle(surface, self.color, (self.pos.x, self.pos.y), self.radius)

# Variables
debugMode = True
massMultiplier = 1
rotateBallsAroundScreen = True
wallBorders = False
flingForceMult = .07
ballDrag = .01
dynamicCollMult = .0000007
balls: list[Ball] = []
selectedBall: Ball = None
isFlinging = False
mousePos: Vector2 = Vector2(0, 0)
###########
# Idk maybe remove this
groundFriction = .025
bounceRedution = .4
gravity = Vector2(0, .005)

# Create some balls
radius = 25
balls.append(Ball(Vector2(WIDTH/2 - radius*4, HEIGHT/2 - radius), radius, RED, name="Left"))
balls.append(Ball(Vector2(WIDTH/2 + radius*4, HEIGHT/2 - radius), radius, GREEN, name="Right"))
numBalls = 150
for i in range(1, numBalls+1):
    ball = Ball(Vector2(randint(100, WIDTH-100), randint(100, HEIGHT-100)), randint(5, 15), (randint(0, 255), randint(0, 255), randint(0, 255)))
    balls.append(ball)
balls.append(Ball(Vector2(WIDTH/2, HEIGHT/2), 150, RED, name="Big Mover"))

while True:
    mPos = pygame.mouse.get_pos()
    mousePos.x = mPos[0]
    mousePos.y = mPos[1]

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    # Check for mouse input
    leftButtonPressed, middleButtonPressed, rightButtonPressed = pygame.mouse.get_pressed(3)

    # Drag ball on left button pressed
    if leftButtonPressed:
        if not selectedBall:
            checkForSelectedBall()
        else:
            # Update selected ball position
            selectedBall.pos.x = clamp(mousePos.x, selectedBall.radius, WIDTH-selectedBall.radius)
            selectedBall.pos.y = clamp(mousePos.y, selectedBall.radius, HEIGHT-selectedBall.radius)
            selectedBall.vel.x = 0
            selectedBall.vel.y = 0
            selectedBall.acc.x = 0
            selectedBall.acc.y = 0       
    elif selectedBall and not isFlinging:
        selectedBall = None

    # Fling ball on right button released
    if rightButtonPressed and not leftButtonPressed:
        if not selectedBall:
            checkForSelectedBall()
            if selectedBall:
                isFlinging = True
    elif selectedBall and not leftButtonPressed:
        # Apply force
        forceDirection = (selectedBall.pos - mousePos) * flingForceMult
        selectedBall.vel = forceDirection
        selectedBall = None
        isFlinging = False

    # Keep track of balls that collided with another
    collidingBallPairs: list[tuple[Ball, Ball]] = []

    # Update balls position
    for ball in balls:
        ball.update()

    # Static collisions
    for i in range(len(balls)-1):
        for j in range(i+1, len(balls)):
            ball1 = balls[i]
            ball2 = balls[j]

            # Check for overlap
            if ball1.checkBallOverlap(ball2):
                # Distance between balls
                distance = ((ball1.pos.x - ball2.pos.x)**2 + (ball1.pos.y - ball2.pos.y)**2)**.5
                if distance == 0:
                    continue

                collidingBallPairs.append((ball1, ball2))

                overlap = (distance - ball1.radius - ball2.radius) * .5
                if overlap*2 > -1:
                    continue

                # Displace ball1
                ball1.pos.x -= overlap * (ball1.pos.x - ball2.pos.x) / distance
                ball1.pos.y -= overlap * (ball1.pos.y - ball2.pos.y) / distance

                # Displace ball2
                ball2.pos.x += overlap * (ball1.pos.x - ball2.pos.x) / distance
                ball2.pos.y += overlap * (ball1.pos.y - ball2.pos.y) / distance

    # Dynamic collisions
    for ballPair in collidingBallPairs:
        ball1 = ballPair[0]
        ball2 = ballPair[1]

        # Distance between balls
        distance = distanceTo(ball1.pos, ball2.pos)
        if distance == 0:
            print("Distance is zero")
            continue

        # Normal
        nX = ball2.pos.x - ball1.pos.x / distance
        nY = ball2.pos.y - ball1.pos.y / distance

        # Tangent
        tX = -nY
        tY = nX

        # Dot product tangent
        dpTan1 = ball1.vel.x * tX + ball1.vel.y * tY
        dpTan2 = ball2.vel.x * tX + ball2.vel.y * tY

        # Dot product normal
        dpNormal1 = ball1.vel.x * nX + ball1.vel.y * nY
        dpNormal2 = ball2.vel.x * nX + ball2.vel.y * nY

        # Conservation for momentum in 1D
        m1 = (dpNormal1 * (ball1.mass - ball2.mass) + 2 * ball2.mass * dpNormal2) / (ball1.mass + ball2.mass)
        m2 = (dpNormal2 * (ball2.mass - ball1.mass) + 2 * ball1.mass * dpNormal1) / (ball1.mass + ball2.mass)

        ball1.vel.x = tX * dpTan1 + nX * m1
        ball1.vel.y = tY * dpTan1 + nY * m1
        ball2.vel.x = tX * dpTan2 + nX * m2
        ball2.vel.y = tY * dpTan2 + nY * m2
        ball1.vel *= dynamicCollMult
        ball2.vel *= dynamicCollMult

    # Clear screen
    window.fill(WHITE)

    # Draw all balls
    for ball in balls:
        ball.applyForce(gravity)
        ball.draw()

    # Draw information when debug mode is active
    if debugMode:
        # Draw collision lines
        for ballPair in collidingBallPairs:
            pygame.draw.line(window, RED, (ballPair[0].pos.x, ballPair[0].pos.y), (ballPair[1].pos.x, ballPair[1].pos.y), 2)

    # Draw sling line
    if rightButtonPressed and not leftButtonPressed and selectedBall:
        pygame.draw.line(window, BLUE, (mousePos.x, mousePos.y), (selectedBall.pos.x, selectedBall.pos.y), 2)

    pygame.display.update()
    clock.tick(FPS)