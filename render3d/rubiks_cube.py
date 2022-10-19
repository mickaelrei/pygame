import pygame
from pygame.locals import *
import sys
sys.dont_write_bytecode = True
from pygame.math import Vector2, Vector3
from random import randint
from math import cos, pi, sin, radians, inf
from time import time
import rendering3d

rendering3d.orthographicProjection = False

pygame.init()
WIDTH = 800
HEIGHT = 800
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

def sortcubes(cubes: list[rendering3d.Cube]):
    for i in range(len(cubes)):
        for j in range(0, len(cubes) - i - 1):
            if cubes[j].pos.z < cubes[j + 1].pos.z:
                temp = cubes[j]
                cubes[j] = cubes[j+1]
                cubes[j+1] = temp

def drawText(text: str, pos: Vector2, fontSize: int=18, fontType: str="comicsans", bold: bool=False,
             italic: bool=False, antiAlias: bool=False, textColor: tuple=BLACK, bgColor: tuple=None,
             centerX: float=0, centerY: float=0, surface: pygame.Surface=window):
    font = pygame.font.SysFont(fontType, fontSize, bold, italic)
    textSurface = font.render(str(text), antiAlias, textColor, bgColor)
    textRect = textSurface.get_rect()
    surface.blit(textSurface, [pos.x + (textRect.width/2) * centerX, pos.y + (textRect.height/2) * centerY])

class RubiksCube:
    def __init__(self, pos: Vector3, cubieSize: float, dimensions: int=3) -> None:
        self.pos = pos
        self.cubieSize = cubieSize
        self.dimensions = dimensions
        self.rotation = Vector3(0, 0, 0)
        self.cubes: list[list[list[rendering3d.Cube]]] = []

        self.faceColors = [
            RED,
            GREEN,
            BLUE,
            WHITE,
            YELLOW,
            ORANGE,
        ]
        for x in range(self.dimensions):
            xList: list[list[rendering3d.Cube]] = []
            for y in range(self.dimensions):
                yList: list[rendering3d.Cube] = []
                for z in range(self.dimensions):
                    cubePos = Vector3(self.pos.x - self.cubieSize/2 + x * self.cubieSize/2, self.pos.y - self.cubieSize/2 +  y * self.cubieSize/2, self.pos.z - self.cubieSize/2 +  z * self.cubieSize/2)
                    cube = rendering3d.Cube(cubePos, self.cubieSize, faceColors=self.faceColors)
                    yList.append(cube)
                    #self.cubes.append(cube)
                xList.append(yList)
            self.cubes.append(xList)

    def rotateCubeX(self, angle: float) -> None:
        pass

    def rotateCubeY(self, angle: float) -> None:
        pass

    def rotateCubeZ(self, angle: float) -> None:
        pass

    def rotateRowX(self, angle: float, xIdx: int=0) -> None:
        self.rotation.x += angle
        # Update all cubes
        cosA = cos(radians(angle))
        sinA = sin(radians(angle))
        for y in range(self.dimensions):
            for z in range(self.dimensions):
                cube = self.cubes[xIdx][y][z]
                cube.rotateX(angle)
                posY = cosA * (cube.pos.y - self.pos.y) - sinA * (cube.pos.z - self.pos.z) + self.pos.y
                posZ = sinA * (cube.pos.y - self.pos.y) + cosA * (cube.pos.z - self.pos.z) + self.pos.z
                cube.pos.y = posY
                cube.pos.z = posZ

    def rotateRowY(self, angle: float, yIdx: int=0) -> None:
        self.rotation.y += angle
        # Update all cubes
        cosA = cos(radians(angle))
        sinA = sin(radians(angle))
        for x in range(self.dimensions):
            for z in range(self.dimensions):
                cube = self.cubes[x][yIdx][z]
                cube.rotateY(-angle)
                posX = sinA * (cube.pos.x - self.pos.x) - cosA * (cube.pos.z - self.pos.z) + self.pos.x
                posZ = cosA * (cube.pos.x - self.pos.x) + sinA * (cube.pos.z - self.pos.z) + self.pos.z
                cube.pos.x = posX
                cube.pos.z = posZ

    def rotateRowZ(self, angle: float, zIdx: int=0) -> None:
        self.rotation.z += angle
        # Update all cubes
        cosA = cos(radians(angle))
        sinA = sin(radians(angle))
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                cube = self.cubes[x][y][zIdx]
                cube.rotateZ(angle)
                posX = cosA * (cube.pos.x - self.pos.x) - sinA * (cube.pos.y - self.pos.y) + self.pos.x
                posY = sinA * (cube.pos.x - self.pos.x) + cosA * (cube.pos.y - self.pos.y) + self.pos.y
                cube.pos.x = posX
                cube.pos.y = posY

    def updateCubes(self) -> None:
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                for z in range(self.dimensions):
                    self.cubes[x][y][z].pos = Vector3(self.pos.x - self.cubieSize/2 + x * self.cubieSize/2, self.pos.y - self.cubieSize/2 +  y * self.cubieSize/2, self.pos.z +  z * self.cubieSize/2)

    def getCubes(self) -> list[rendering3d.Cube]:
        cubes: list[rendering3d.Cube] = []
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                for z in range(self.dimensions):
                    cubes.append(self.cubes[x][y][z])
        return cubes

    def draw(self, surface: pygame.Surface=window, drawEdges: bool=True) -> None:
        # self.rotateRowX(1, 0)
        # self.rotateRowY(1, 0)
        # self.rotateRowZ(1, 0)

        cubes = self.getCubes()
        sortcubes(cubes)

        for cube in cubes:
            cube.draw(surface, drawEdges=drawEdges, paintFaces=True)

rubiksCube = RubiksCube(Vector3(WIDTH/2, HEIGHT/2, 0), 150)
#rubiksCube.rotateRowX(5, 0)
#rubiksCube.rotateRowX(5, 1)
#rubiksCube.rotateRowX(5, 2)

while True:
    # Mouse input
    left, middle, right = pygame.mouse.get_pressed()
    leftButtonDown, rightButtonDown = left, right

    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEMOTION:
            if leftButtonDown:
                rendering3d.translate(event.rel[0], event.rel[1], 0)
            if rightButtonDown:
                rendering3d.rotate(event.rel[1], event.rel[0], 0)
        elif event.type == KEYDOWN:
            if event.key == K_q:
                rubiksCube.rotateRowX(90, 0)
            elif event.key == K_w:
                rubiksCube.rotateRowX(90, 1)
            elif event.key == K_e:
                rubiksCube.rotateRowX(90, 2)
            elif event.key == K_a:
                rubiksCube.rotateRowZ(90, 0)
            elif event.key == K_s:
                rubiksCube.rotateRowZ(90, 1)
            elif event.key == K_d:
                rubiksCube.rotateRowZ(90, 2)
            elif event.key == K_z:
                rubiksCube.rotateRowY(90, 0)
            elif event.key == K_x:
                rubiksCube.rotateRowY(90, 1)
            elif event.key == K_c:
                rubiksCube.rotateRowY(90, 2)

    window.fill(WHITE)
    
    rubiksCube.draw(surface=window, drawEdges=True)

    # Show FPS
    drawText(f"FPS: {clock.get_fps():.0f}", Vector2(), fontSize=15)

    pygame.display.update()
    clock.tick(FPS)

'''
TODO:
 - Botar pra funcionar com orthographic projection (aumentar o espaçamento entre os cubies)
 - Aplicar rotação do próprio rubiksCube para cada cubo
'''