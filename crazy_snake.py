import pygame, sys
from pygame.locals import *
from pygame.math import Vector2
from math import sin, cos, radians, floor

pygame.init()

WIDTH = 600
HEIGHT = 600
FPS = 6000
dt = 0
move_tick = 0
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
CYAN = (255, 0, 255)

class PathSection:
    def __init__(self, lifetime: float=15) -> None:
        self.hue = (move_tick * 90) % 360
        self.lifetime = lifetime
        self.life = 0

    def getColor(self) -> pygame.Color:
        # Get color based on lifetime
        color = pygame.Color(0, 0, 0, 0)
        color.hsla = (self.hue, 100, 50, floor((1 - self.life / self.lifetime) * 100))

        return color

    def update(self) -> bool:
        self.life += dt
        self.hue = (self.hue + dt * 0) % 360

        # Returns if it's still alive
        return self.life < self.lifetime

class CirclePathSection(PathSection):
    def __init__(self, pos: Vector2, size: float, angle: float, lifetime: float=3) -> None:
        super().__init__(lifetime)
        self.pos = pos
        self.size = size

    def draw(self) -> None:
        color = self.getColor()

        # Create circle surface
        circleSurface = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(circleSurface, color, (self.size, self.size), self.size)

        # Blit circle surface
        window.blit(circleSurface, (floor(self.pos.x - self.size), floor(self.pos.y - self.size)))

class LinePathSection(PathSection):
    def __init__(self, startPos: Vector2, endPos: Vector2, lifetime: float=5) -> None:
        super().__init__(lifetime)
        self.startPos = startPos
        self.endPos = endPos
        self.diffX = abs(startPos.x - endPos.x)
        self.diffY = abs(startPos.y - endPos.y)
        self.surfaceSize = max(self.diffX, self.diffY)

        self.minX = min(self.startPos.x, self.endPos.x)
        self.minY = min(self.startPos.y, self.endPos.y)
        self.maxX = max(self.startPos.x, self.endPos.x)
        self.maxY = max(self.startPos.y, self.endPos.y)

    def draw(self) -> None:
        color = self.getColor()

        # Create line surface
        x1 = self.startPos.x - self.minX
        y1 = self.startPos.y - self.minY
        x2 = self.endPos.x - self.minX
        y2 = self.endPos.y - self.minY
        lineSurface = pygame.Surface((self.surfaceSize, self.surfaceSize), pygame.SRCALPHA)
        pygame.draw.line(lineSurface, color, (x1, y1), (x2, y2), 15)

        # Blit circle surface
        window.blit(lineSurface, (self.minX, self.minY))

class Particle:
    def __init__(self, pos: Vector2, vel: float=150, startAngle: float=0, color: tuple=WHITE, size: float=15, rotationSpeed: float=150) -> None:
        self.pos = pos
        self.vel = vel
        self.angle = startAngle
        self.rotationSpeed = rotationSpeed
        self.size = size
        self.color = color
        self.path: list[PathSection] = []

    def move(self, speedMult: float=1) -> None:
        x = cos(radians(self.angle)) * self.vel * speedMult * dt
        y = sin(radians(self.angle)) * self.vel * speedMult * dt
        self.pos += Vector2(x, y)

        if x != 0 or y != 0:
            global move_tick
            move_tick += dt

            print("Adding path section")
            # Add path section
            if circlePath:
                section = CirclePathSection(Vector2(self.pos), self.size, self.angle, lifetime=pathLifetime)
            else:
                startAngle = self.angle - 90
                endAngle = self.angle + 90
                x1 = self.pos.x + cos(radians(startAngle)) * self.size
                y1 = self.pos.y + sin(radians(startAngle)) * self.size
                x2 = self.pos.x + cos(radians(endAngle)) * self.size
                y2 = self.pos.y + sin(radians(endAngle)) * self.size
                section = LinePathSection(Vector2(x1, y1), Vector2(x2, y2), lifetime=pathLifetime)
            self.path.append(section)

    def rotate(self, rotationMult: float=1) -> None:
        self.angle += self.rotationSpeed * rotationMult * dt

    def draw(self) -> None:
        # Draw path
        for section in self.path[:]:
            alive = section.update()
            if not alive:
                self.path.remove(section)
                continue

            section.draw()

        x = self.pos.x + cos(radians(self.angle)) * self.size
        y = self.pos.y + sin(radians(self.angle)) * self.size
        pygame.draw.circle(window, self.color, self.pos, self.size)
        pygame.draw.line(window, RED, self.pos, (x, y), 1)

circlePath = True
pathLifetime = 5
plr = Particle(Vector2(WIDTH/2, HEIGHT/2))
moveInput = Vector2()
while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_w or event.key == K_UP:
                moveInput.x += 1
            elif event.key == K_s or event.key == K_DOWN:
                moveInput.x -= 1
            elif event.key == K_a or event.key == K_LEFT:
                moveInput.y += 1
            elif event.key == K_d or event.key == K_RIGHT:
                moveInput.y -= 1
        elif event.type == KEYUP:
            if event.key == K_w or event.key == K_UP:
                moveInput.x -= 1
            elif event.key == K_s or event.key == K_DOWN:
                moveInput.x += 1
            elif event.key == K_a or event.key == K_LEFT:
                moveInput.y -= 1
            elif event.key == K_d or event.key == K_RIGHT:
                moveInput.y += 1
            
    window.fill(BLACK)

    plr.move(moveInput.x)
    plr.rotate(-moveInput.y)
    plr.draw()

    pygame.display.set_caption(f"Crazy Snake | FPS: {clock.get_fps():.0f}")
    pygame.display.update()
    dt = clock.tick(FPS) / 1000
