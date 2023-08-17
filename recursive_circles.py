import pygame, sys
from math import cos, sin, radians

pygame.init()

WIDTH = 1300
HEIGHT = 600
FPS = 6000
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

a = 50
def drawCircle(x, y, r):
    pygame.draw.circle(window, WHITE, (x, y), r, 1)
    if r > 5:
        newX = cos(radians(a)) * r
        newY = sin(radians(a)) * r
        drawCircle(x + newX, y + newY, r/2)
        drawCircle(x - newX, y - newY, r/2)
        drawCircle(x - newY, y + newX, r/2)
        drawCircle(x + newX, y - newY, r/2)

        drawCircle(x + newX, y + newY, r/2)
        drawCircle(x - newX, y - newY, r/2)
        drawCircle(x - newX, y + newY, r/2)
        drawCircle(x + newX, y - newY, r/2)

        # drawCircle(x - r, y, r/2)
        # drawCircle(x + r, y, r/2)
        # drawCircle(x, y - r, r/2)
        # drawCircle(x, y + r, r/2)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

    window.fill(BLACK)
    drawCircle(WIDTH/2, HEIGHT/2, 150)
    a = pygame.mouse.get_pos()[0] / WIDTH * 360

    pygame.display.set_caption(f"FPS: {clock.get_fps():.0f}")
    pygame.display.update()
    clock.tick(FPS)