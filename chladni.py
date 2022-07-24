import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from math import inf, cos
from random import randint, random
from time import time

##############################
# Chladni customization
numParticles = 5000
vibration = 4
scale = 1
changePatternDelay = 1e10
minVibrationToMove = .01

pygame.init()
WIDTH = 200
HEIGHT = 200
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 6000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (127, 0, 255)

class ChladniParams:
    M: float
    N: float
    L: float

    def __init__(self, m: float, n: float, l: float) -> None:
        self.M = m
        self.N = n
        self.L = l

params: list[ChladniParams] = [
    # ChladniParams(5, 4, .02),
    # ChladniParams(3, 7, .02),
    # ChladniParams(2, 3, .02),
    # ChladniParams(4, 3, .02),
    # ChladniParams(4, 3, .06),
    ChladniParams(m, n, .03) for m in range(5, 1, -1) for n in range(1, 5) if (m > n)
]

# Helper functions
def sign(x: float) -> int:
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0

def clamp(x: float, minV: float, maxV: float) -> float:
    if x > maxV:
        return maxV
    elif x < minV:
        return minV
    else:
        return x

class Particle:
    def __init__(self, pos: Vector2, color: tuple=BLACK, size: float=1) -> None:
        self.pos = pos
        self.color = color
        self.size = size

    def draw(self, surface: pygame.Surface=window) -> None:
        pygame.draw.circle(surface, self.color, self.pos, self.size)

class ChladniPlate:
    def __init__(self, numParticles: int=500, scale: float=2, particleColor: tuple=BLACK, particleSize: float=1) -> None:
        self.width = WIDTH/scale
        self.height = HEIGHT/scale
        self.scale = scale
        self.showVibrations = False
        self.paused = False
        self.vibrations: list[float] = []
        self.lastFallenParticlesCheck = time()

        # Create particles
        self.particles: list[Particle] = []
        for i in range(numParticles):
            pos = Vector2(randint(0, WIDTH), randint(0, HEIGHT))
            self.particles.append(Particle(pos, particleColor, particleSize))

        # Calculate vibrations once for each pattern
        self.lastPatternChange = time()
        self.currentParamsIndex = 0
        self.computeVibrations(params[self.currentParamsIndex])

    def vibrateParticles(self) -> None:
        # Move particles randomly based on vibration
        for particle in self.particles:
            particle.pos += Vector2((random() -.5) * vibration, (random() -.5) * vibration)

    def moveTowardsPattern(self) -> None:
        # Calculate gradients
        gradients: list[Vector2] = [0] * round(self.width * self.height)
        for y in range(1, round(self.height)-1):
            for x in range(1, round(self.width)-1):
                idx = y * round(self.width) + x
                vibration = self.vibrations[idx]

                if vibration < minVibrationToMove:
                    gradients[idx] = Vector2(0, 0)
                    continue

                minVibration = inf
                candidates: list[Vector2] = []
                for ny in range(-1, 2):
                    for nx in range(-1, 2):
                        if ny == 0 and nx == 0:
                            continue

                        nIdx = (y + ny) * round(self.width) + (x + nx)
                        nVibration = self.vibrations[nIdx]

                        # if neighbor has *same* vibration as minimum so far, consider it as well to avoid biasing
                        if nVibration <= minVibration:
                            if nVibration < minVibration:
                                minVibration = nVibration
                                candidates = []
                            
                            candidates.append(Vector2(nx, ny))

                chosenCandidate = candidates[randint(0, len(candidates)-1)]
                gradients[idx] = chosenCandidate

        # Move particles
        for particle in self.particles:
            idx = round(particle.pos.y / self.scale) * round(self.width) + round(particle.pos.x / self.scale)
            try:
                gradient = gradients[idx]
                particle.pos.x += gradient.x
                particle.pos.y += gradient.y
            except IndexError:
                # print(f"IndexError for particle at pos ({particle.pos.x}, {particle.pos.y})")
                pass
            except AttributeError:
                # print(f"AttributeError for particle at pos ({particle.pos.x}, {particle.pos.y})")
                pass

    def update(self) -> None:
        if self.paused:
            return

        # Vibrate particles
        self.vibrateParticles()
        self.moveTowardsPattern()

        # Reposition fallen particles
        if time() > self.lastFallenParticlesCheck + 10:
            self.lastFallenParticlesCheck = time()
            self.checkFallenParticles()

        # Check if need to change pattern
        if time() > self.lastPatternChange + changePatternDelay:
            self.nextPattern()

    def nextPattern(self) -> None:
        self.lastPatternChange = time()
        self.currentParamsIndex = (self.currentParamsIndex + 1) % len(params)
        self.computeVibrations(params[self.currentParamsIndex])

    def checkFallenParticles(self, offScreenLimit: float=50) -> None:
        for particle in self.particles:
            if (particle.pos.x < -offScreenLimit or particle.pos.x > WIDTH + offScreenLimit or
                particle.pos.y < -offScreenLimit or particle.pos.y > HEIGHT + offScreenLimit):
                particle.pos = Vector2(randint(0, WIDTH), randint(0, HEIGHT))

    def computeVibrations(self, chladniParams: ChladniParams):
        M = chladniParams.M
        N = chladniParams.N
        L = chladniParams.L * self.scale
        print(f"New pattern: M={M}, N={N}, L={L}")
        R = 0 #Math.random() * TAU  # turn this on to introduce some asymmetry
        # translate randomly to help spread particles
        TX = 0#random() * self.width
        TY = 0#random() * self.height

        self.vibrations = [0] * round(self.width * self.height)
        for y in range(round(self.height)):
            for x in range(round(self.width)):
                scaledX = x * L + TX
                scaledY = y * L + TY
                # ToDo when scaledX|scaledY > TAU, the pattern repeats - compute it once and just copy it for the rest
                MX = M * scaledX + R
                NX = N * scaledX + R
                MY = M * scaledY + R
                NY = N * scaledY + R

                # Chladni equation
                value = cos(NX) * cos(MY) - cos(MX) * cos(NY)

                # normalize from [-2..2] to [-1..1]
                value /= 2

                # flip troughs to become crests (values map from [-1..1] to [0..1])
                value *= sign(value)

                index = y * round(self.width) + x
                self.vibrations[index] = value
            
    def draw(self, surface: pygame.Surface=window) -> None:
        if self.showVibrations:
            maxLuminosity = 60

            for y in range(round(self.height)):
                for x in range(round(self.width)):
                    idx = y * round(self.width) + x
                    vibration = self.vibrations[idx]
                    colorLuminosity = clamp(vibration * maxLuminosity, 0, 255)

                    # Paint cell
                    pygame.draw.circle(surface, (colorLuminosity, colorLuminosity, colorLuminosity), (x * self.scale, y * self.scale), self.scale)
                    # for cy in range(round(self.scale)):
                    #     for cx in range(round(self.scale)):
                    #         surface.set_at((x * self.scale + cx, y * self.scale + cy), (colorLuminosity, colorLuminosity, colorLuminosity))

            # print(f"Min: {minV:.4f}, Max: {maxV:.4f}")

        for particle in self.particles:
            particle.draw(surface)


plate = ChladniPlate(numParticles=numParticles, scale=scale, particleColor=PURPLE)

while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_d:
                plate.showVibrations = not plate.showVibrations
            elif event.key == K_SPACE:
                plate.paused = not plate.paused
            elif event.key == K_f:
                plate.nextPattern()

    window.fill(BLACK)

    plate.update()
    plate.draw()

    pygame.display.update()
    pygame.display.set_caption(f"Chladni Plate | FPS: {clock.get_fps():.0f}")
    clock.tick(FPS)