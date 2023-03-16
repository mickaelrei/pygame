import pygame, sys
from pygame.locals import *
from pygame.math import Vector2
from math import sin, cos, radians, floor

pygame.init()

WIDTH = 600
HEIGHT = 600
FPS = 6000
dt = 0
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
CYAN = (255, 0, 255)

class PathSection:
    def __init__(self, pos: Vector2, size: float, angle: float, lifetime: float=15, color: tuple=CYAN) -> None:
        self.pos = pos
        self.size = size
        self.color = color
        self.hue = (pygame.time.get_ticks() / 1000) % 360
        self.lifetime = lifetime
        self.life = 0

    def update(self) -> bool:
        self.life += dt
        self.hue = (self.hue + dt * 1e6) % 360

        # Returns if it's still alive
        return self.life < self.lifetime

    def draw(self) -> None:
        # Get color based on lifetime
        color = pygame.Color(self.color[0], self.color[1], self.color[2], floor((1 - self.life / self.lifetime) * 100))
        color.hsla = (self.hue, 100, 50, floor((1 - self.life / self.lifetime) * 100))
        # Create circle surface
        circleSurface = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(circleSurface, color, (self.size, self.size), self.size)

        # Blit circle surface
        window.blit(circleSurface, (floor(self.pos.x - self.size), floor(self.pos.y - self.size)))

class Particle:
    def __init__(self, pos: Vector2, vel: float=500, startAngle: float=0, color: tuple=WHITE, size: float=15, rotationSpeed: float=750) -> None:
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

        if x != 0 and y != 0:
            # Add path section
            section = PathSection(Vector2(self.pos), self.size, self.angle)
            self.path.append(section)

    def rotate(self, rotationMult: float=1) -> None:
        self.angle += self.rotationSpeed * rotationMult * dt

    def draw(self) -> None:
        print(self.angle)
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

    pygame.display.update()
    dt = clock.tick(FPS) / 1000
