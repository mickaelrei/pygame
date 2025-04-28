import pygame
import sys
import math
from pygame.math import Vector2

pygame.init()

WIDTH = 600
HEIGHT = 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
clock = pygame.time.Clock()

RED = (255, 0, 0)
ORANGE = (255, 127, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (40, 40, 40)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

TILE_SIZE = 40
NUM_TILES_X = WIDTH // TILE_SIZE
NUM_TILES_Y = HEIGHT // TILE_SIZE
GRID = [[0 for _ in range(NUM_TILES_X)] for _ in range(NUM_TILES_Y)]

def vectorTileToWorld(v: Vector2):
    return Vector2(v.x * TILE_SIZE, v.y * TILE_SIZE)

def vectorWorldToTile(v: Vector2):
    return Vector2(v.x // TILE_SIZE, v.y // TILE_SIZE)

def tileToWorld(x: int):
    return x * TILE_SIZE

def worldToTile(x: float):
    return int(x // TILE_SIZE)

class RaycastResult:
    def __init__(self,  position: Vector2, normal: Vector2):
        self.position = position
        self.normal = normal

    def __repr__(self):
        return f"RaycastResult(position={self.position}, normal={self.normal})"

def raycastVertical(rayStart: Vector2, rayDir: Vector2, maxDistance: float):
    # Current ray position in tile coordinates
    mapCheck = vectorWorldToTile(rayStart)

    # Multiplier for ray direction
    step = 0

    # How much the ray has traveled
    rayLength = 0
    if rayDir.y < 0:
        step = -1
        rayLength = (rayStart.y - tileToWorld(mapCheck.y))
    else:
        step = 1
        rayLength = (tileToWorld(mapCheck.y + 1) - rayStart.y)

    # Keep moving the ray until it hits a wall or exceeds maxDistance
    distance = 0
    while distance < maxDistance:
        # Move the ray in the y direction
        mapCheck.y += step
        distance = rayLength
        rayLength += tileToWorld(1)

        # Check if we have exceeded the max distance
        if distance >= maxDistance:
            return None
        
        # Ensure ray is within the bounds of the grid
        if mapCheck.x < 0 or mapCheck.x >= NUM_TILES_X or mapCheck.y < 0 or mapCheck.y >= NUM_TILES_Y:
            continue

        # Check if the ray has hit a wall
        if GRID[int(mapCheck.y)][int(mapCheck.x)] == 1:
            return RaycastResult(rayStart + rayDir * distance, Vector2(0, -step))

    # If we got here ray didn't hit anything
    return None

def raycastHorizontal(rayStart: Vector2, rayDir: Vector2, maxDistance: float):
    # Current ray position in tile coordinates
    mapCheck = vectorWorldToTile(rayStart)

    # Multiplier for ray direction
    step = 0

    # How much the ray has traveled
    rayLength = 0
    if rayDir.x < 0:
        step = -1
        rayLength = (rayStart.x - tileToWorld(mapCheck.x))
    else:
        step = 1
        rayLength = (tileToWorld(mapCheck.x + 1) - rayStart.x)

    # Keep moving the ray until it hits a wall or exceeds maxDistance
    distance = 0
    while distance < maxDistance:
        # Move the ray in the x direction
        mapCheck.x += step
        distance = rayLength
        rayLength += tileToWorld(1)

        # Check if we have exceeded the max distance
        if distance >= maxDistance:
            return None

        # Ensure ray is within the bounds of the grid
        if mapCheck.x < 0 or mapCheck.x >= NUM_TILES_X or mapCheck.y < 0 or mapCheck.y >= NUM_TILES_Y:
            continue

        # Check if the ray has hit a wall
        if GRID[int(mapCheck.y)][int(mapCheck.x)] == 1:
            return RaycastResult(rayStart + rayDir * distance, Vector2(-step, 0))

    # If we got here ray didn't hit anything
    return None

def raycast(rayStart: Vector2, rayDir: Vector2, maxDistance: float):
    # Null direction or negative/zero distance
    if rayDir.length_squared() == 0 or maxDistance <= 0:
        return None
    rayDir = rayDir.normalize()

    # Current ray position in tile coordinates
    mapCheck = vectorWorldToTile(rayStart)

    # If we start inside a wall, return None
    if mapCheck.x >= 0 and mapCheck.x < NUM_TILES_X and mapCheck.y >= 0 and mapCheck.y < NUM_TILES_Y:
        if GRID[int(mapCheck.y)][int(mapCheck.x)] == 1:
            return None

    # Edge case: ray is perfectly vertical or horizontal; calculating
    # unitStepSize would cause a division by zero
    if rayDir.x == 0:
        return raycastVertical(rayStart, rayDir, maxDistance)
    if rayDir.y == 0:
        return raycastHorizontal(rayStart, rayDir, maxDistance)

    # How much the ray travels in each coordinate
    unitStepSize = Vector2(
        math.sqrt(1 + (rayDir.y / rayDir.x)**2),
        math.sqrt(1 + (rayDir.x / rayDir.y)**2)
    )

    # Multiplier for ray direction
    step = Vector2(0, 0)

    # How much the ray has traveled in each coordinate
    rayLength = Vector2(0, 0)
    if rayDir.x < 0:
        step.x = -1
        rayLength.x = (rayStart.x - tileToWorld(mapCheck.x)) * unitStepSize.x
    else:
        step.x = 1
        rayLength.x = (tileToWorld(mapCheck.x + 1) - rayStart.x) * unitStepSize.x

    if rayDir.y < 0:
        step.y = -1
        rayLength.y = (rayStart.y - tileToWorld(mapCheck.y)) * unitStepSize.y
    else:
        step.y = 1
        rayLength.y = (tileToWorld(mapCheck.y + 1) - rayStart.y) * unitStepSize.y

    # Keep moving the ray until it hits a wall or exceeds maxDistance
    distance = 0
    while distance < maxDistance:
        movedX = False
        if rayLength.x < rayLength.y:
            # Move the ray in the x direction
            movedX = True
            mapCheck.x += step.x
            distance = rayLength.x
            rayLength.x += tileToWorld(unitStepSize.x)
        else:
            # Move the ray in the y direction
            mapCheck.y += step.y
            distance = rayLength.y
            rayLength.y += tileToWorld(unitStepSize.y)

        # Check if we have exceeded the max distance
        if distance >= maxDistance:
            return None
        
        # If ray is out of grid bounds, continue moving
        if mapCheck.x < 0 or mapCheck.x >= NUM_TILES_X or mapCheck.y < 0 or mapCheck.y >= NUM_TILES_Y:
            continue

        # Check if the ray has hit a wall
        if GRID[int(mapCheck.y)][int(mapCheck.x)] == 1:
            if movedX:
                # We hit a vertical wall
                normal = Vector2(-step.x, 0)
            else:
                # We hit a horizontal wall
                normal = Vector2(0, -step.y)

            return RaycastResult(rayStart + rayDir * distance, normal)

    # If we got here ray didn't hit anything
    return None

# Create a grid with some walls
for j in range(NUM_TILES_Y):
    for i in range(NUM_TILES_X):
        center_x = NUM_TILES_X // 2 - 0.5
        center_y = NUM_TILES_Y // 2 - 0.5
        distance = math.sqrt((i - center_x) ** 2 + (j - center_y) ** 2)
        if abs(distance - NUM_TILES_X / 3) < 0.5:
            GRID[j][i] = 1

rayStart = Vector2(WIDTH // 2, HEIGHT // 2)
moveSpeed = 5
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        rayStart.y -= moveSpeed
    if keys[pygame.K_s]:
        rayStart.y += moveSpeed
    if keys[pygame.K_a]:
        rayStart.x -= moveSpeed
    if keys[pygame.K_d]:
        rayStart.x += moveSpeed

    WINDOW.fill(BLACK)

    # Draw a grid of tiles
    for j in range(NUM_TILES_Y):
        for i in range(NUM_TILES_X):
            value = GRID[j][i]
            x = i * TILE_SIZE
            y = j * TILE_SIZE
            if value == 1:
                pygame.draw.rect(WINDOW, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
            else:
                pygame.draw.rect(WINDOW, GREY, (x, y, TILE_SIZE, TILE_SIZE))
            # pygame.draw.rect(WINDOW, WHITE, (x, y, TILE_SIZE, TILE_SIZE), 1)

    # Draw the ray start position
    pygame.draw.circle(WINDOW, RED, (int(rayStart.x), int(rayStart.y)), 5)

    # Draw circle at mouse position
    mousePos = Vector2(pygame.mouse.get_pos())
    pygame.draw.circle(WINDOW, GREEN, (int(mousePos.x), int(mousePos.y)), 5)

    # Get ray direction
    rayDir = mousePos - rayStart
    length = rayDir.length()
    if length > 0:
        # Raycast in the direction of the mouse
        result = raycast(rayStart, rayDir, length)
        if result is not None:
            pygame.draw.circle(WINDOW, ORANGE, result.position, 7, 3)
            pygame.draw.line(WINDOW, GREEN, result.position, result.position + result.normal * 50, 2)

        pygame.draw.line(WINDOW, WHITE, rayStart, rayStart + rayDir, 1)

    pygame.display.update()
    clock.tick(FPS)