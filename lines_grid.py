import pygame
import sys
import math
from pygame.math import Vector2

WIDTH = 600
HEIGHT = 600
FPS = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Customization parameters
COLS = 11
ROWS = 11
SIZE = 50

# Calculate top left position
TOP_LEFT = Vector2(WIDTH / 2, HEIGHT / 2)
TOP_LEFT.x -= (COLS / 2 - 0.5) * SIZE
TOP_LEFT.y -= (ROWS / 2 - 0.5) * SIZE

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

    window.fill(BLACK)

    # Mouse pos
    mx, my = pygame.mouse.get_pos()
    
    for i in range(COLS):
        for j in range(ROWS):
            # Line center
            center = TOP_LEFT + Vector2(i * SIZE, j * SIZE)

            # Angle between line center and mouse pos
            dx = mx - center.x
            dy = my - center.y
            angle = math.atan2(dy, dx) + math.pi / 2

            # Calculate the line's both ends
            offx = SIZE / 2 * math.cos(angle)
            offy = SIZE / 2 * math.sin(angle)
            p0 = center + Vector2(offx, offy)
            p1 = center - Vector2(offx, offy)

            pygame.draw.aaline(window, WHITE, p0, p1, 2)
    
    pygame.display.update()
    clock.tick(FPS)