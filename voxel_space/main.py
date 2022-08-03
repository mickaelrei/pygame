import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from random import randint
from math import atan2, cos, floor, inf, radians, sin
from time import time
import os.path

pathFile = os.path.dirname(__file__)

pygame.init()
WIDTH = 300
HEIGHT = 300
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 6000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 127, 0)

# Function to load color and height maps
def loadMaps(colorMapFile: str, heightMapFile: str) -> tuple[list[list[Color]], list[list[int]]]:
    # Load surfaces
    colorMap = pygame.image.load(os.path.join(pathFile, colorMapFile))
    heightMap = pygame.image.load(os.path.join(pathFile, heightMapFile))

    # Get sizes
    colorMapSize = colorMap.get_size()
    heightMapSize = heightMap.get_size()

    # Save height values
    heightMapList: list[list[int]] = []
    for y in range(heightMapSize[1]):
        line: list[int] = []
        for x in range(heightMapSize[0]):
            line.append(heightMap.get_at((x, y))[0])

        heightMapList.append(line)

    # Save color values
    colorMapList: list[list[tuple[int, int, int]]] = []
    for y in range(colorMapSize[1]):
        line: list[tuple[int, int, int]] = []
        for x in range(colorMapSize[0]):
            line.append(colorMap.get_at((x, y)))

        colorMapList.append(line)

    return colorMapList, heightMapList

def checkInput():
    global moveDelta, rotationDelta, pitchDelta, heightDelta
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in (K_w, K_UP):
                moveDelta -= moveSpeed
            elif event.key in (K_s, K_DOWN):
                moveDelta += moveSpeed
            elif event.key in (K_d, K_RIGHT):
                # moveDelta += Vector2(1, 0)
                rotationDelta -= rotationSpeed
            elif event.key in (K_a, K_LEFT):
                # moveDelta += Vector2(-1, 0)
                rotationDelta += rotationSpeed
            elif event.key == K_r:
                pitchDelta += pitchSpeed
            elif event.key == K_f:
                pitchDelta -= pitchSpeed
            elif event.key == K_q:
                heightDelta += heightSpeed
            elif event.key == K_e:
                heightDelta -= heightSpeed
            elif event.key == K_c:
                print(POS)
            elif event.key == K_v:
                print(ROTATION)
        elif event.type == KEYUP:
            if event.key in (K_w, K_UP):
                moveDelta += moveSpeed
            elif event.key in (K_s, K_DOWN):
                moveDelta -= moveSpeed
            elif event.key in (K_d, K_RIGHT):
                # moveDelta -= Vector2(1, 0)
                rotationDelta += rotationSpeed
            elif event.key in (K_a, K_LEFT):
                # moveDelta -= Vector2(-1, 0)
                rotationDelta -= rotationSpeed
            elif event.key == K_r:
                pitchDelta -= pitchSpeed
            elif event.key == K_f:
                pitchDelta += pitchSpeed
            elif event.key == K_q:
                heightDelta -= heightSpeed
            elif event.key == K_e:
                heightDelta += heightSpeed

def clamp(x, minimum, maximum):
    if x < minimum:
        return minimum
    elif x > maximum:
        return maximum
    else:
        return x

def getColorAt(colorMap: list[list[int]], x: int, y: int) -> int:
    x = round(x) % len(colorMap[0])
    y = round(y) % len(colorMap)

    return colorMap[y][x]

def getHeightAt(heightMap: list[list[int]], x: int, y: int) -> int:
    # x = clamp(round(x), 0, len(heightMap[0])-1)
    # y = clamp(round(y), 0, len(heightMap)-1)
    x = round(x) % len(heightMap[0])
    y = round(y) % len(heightMap)

    return heightMap[y][x]

def drawVerticalLine(posX: int, yTop: float, yBottom: float, color: tuple):
    pygame.draw.line(window, color, (posX, yTop), (posX, yBottom))
    # if posX % 400 == 0:
    #     checkInput()
    #     pygame.display.update()

# Function to render a line
def renderMap(colorMap: list[list[Color]], heightMap: list[list[int]],
           point: Vector2, heightScale: float, horizon: float, distance: float, distanceScale: float):

    mapSize = Vector2(len(colorMap[0])-1, len(colorMap)-1)
    sinA = sin(radians(ROTATION))
    cosA = cos(radians(ROTATION))

    # Store highest Y values for each screen column
    columnHeights: list[float] = [WIDTH] * WIDTH

    dz = 1
    z = 1
    # for z in range(round(distance), 1, -RENDER_STEP):
    while z < distance:
        pLeft = Vector2(
            (-cosA * z - sinA * z) + point.x,
            ( sinA * z - cosA * z) + point.y)
        pRight = Vector2(
            ( cosA * z - sinA * z) + point.x,
            (-sinA * z - cosA * z) + point.y)

        # if pLeft.x < 0 or pLeft.x > mapSize.x or pLeft.y < 0 or pLeft.y > mapSize.y or pRight.x < 0 or pRight.x > mapSize.x or pRight.y < 0 or pRight.y > mapSize.y:
        #     continue

        dx = (pRight - pLeft).x / WIDTH
        dy = (pRight - pLeft).y / WIDTH

        for x in range(0, WIDTH):
            # print(f"z={z}, x={x}")
            heightOnScreen = (CAMERA_HEIGHT - getHeightAt(heightMap, pLeft.x, pLeft.y)) / 255 * heightScale / z * distanceScale + horizon
            # print(getHeightAt(heightMap, pLeft.x, pLeft.y), heightOnScreen)
            # heightOnScreen = maxHeight - getHeightAt(heightMap, pLeft.x, pLeft.y) * z / scaleHeight + horizon
            drawVerticalLine(x, heightOnScreen, columnHeights[x], getColorAt(colorMap, pLeft.x, pLeft.y))
            if heightOnScreen < columnHeights[x]:
                columnHeights[x] = heightOnScreen
            pLeft.x += dx
            pLeft.y += dy

        z += dz
        dz += .01

def renderFrame():
    window.fill(WHITE)
    renderMap(colorMap, heightMap, POS, heightScale=HEIGHT_SCALE, horizon=HORIZON_HEIGHT, distance=RENDER_DISTANCE, distanceScale=DISTANCE_SCALE)

######################################################
# Variables
colorMapFile = "maps/color0.png"
heightMapFile = "maps/height0.png"
POS = Vector2(440, 250)
ROTATION = 0
moveSpeed = 25
pitchSpeed = 75
rotationSpeed = 45
heightSpeed = 45

moveDelta = 0
pitchDelta = 0
rotationDelta = 0
heightDelta = 0
RENDER_STEP = 4
RENDER_DISTANCE = 800
DISTANCE_SCALE = 300
HORIZON_HEIGHT = 100
HEIGHT_SCALE = 150
CAMERA_HEIGHT = 155

# Get maps
colorMap, heightMap = loadMaps(colorMapFile, heightMapFile)
renderFrame()

while True:
    lastPos = POS.copy()
    checkInput()

    render = False
    if moveDelta != 0:
        # POS += moveDelta.normalize() * moveSpeed
        x = -cos(radians(ROTATION + 90)) * moveDelta
        y = sin(radians(ROTATION + 90)) * moveDelta
        POS.x += x
        POS.y += y
        render = True

    if pitchDelta != 0:
        HORIZON_HEIGHT += pitchDelta / 1000 * clock.get_time()
        render = True

    if rotationDelta != 0:
        ROTATION += rotationDelta / 1000 * clock.get_time()
        render = True

    if heightDelta != 0:
        CAMERA_HEIGHT -= heightDelta / 1000 * clock.get_time()
        render = True

    # print(ROTATION)

    if render:
        renderFrame()

    pygame.display.set_caption(f"Voxel Space | FPS: {clock.get_fps():.0f}")
    pygame.display.update()
    clock.tick(FPS)