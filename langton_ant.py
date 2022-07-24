import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from random import randint, randrange, choice
from math import cos, pi, sin, radians, inf, floor

pygame.init()
WIDTH = 1300
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
CYAN = (255, 0, 255)
PINK = (255, 50, 190)
GRAY = (100, 100, 100)
DARK_RED = (100, 0, 0)
DARK_GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 100)
DARK_YELLOW = (100, 100, 0)
PURPLE = (127, 0, 255)
COLORS = {
    "Red": RED,
    "Green": GREEN,
    "Black": BLACK,
    "White": WHITE,
    "Blue": BLUE,
    "Orange": ORANGE,
    "Cyan": CYAN,
    "Yellow": YELLOW,
    "Pink": PINK,
    "Gray": GRAY,
    "Dark Red": DARK_RED,
    "Dark Green": DARK_GREEN,
    "Dark Blue": DARK_BLUE,
    "Dark Yellow": DARK_YELLOW,
    "Purple": PURPLE,
}

# Customization
CELL_SCALE = 1
LINE_COLOR = (30, 30, 30)

class Directions:
    North = "North"
    South = "South"
    East = "East"
    West = "West"

# Two ways the ants can go
LEFT = "Left"
RIGHT = "Right"

# List of movement rules
RULES = {
    "White": RIGHT,
    "Red": LEFT,
    "Green": LEFT,
    "Cyan": RIGHT,
    "Yellow": RIGHT,
    "Pink": LEFT,
    "Gray": RIGHT,
    "Dark Red": RIGHT,
    "Dark Green": RIGHT,
    "Dark Blue": RIGHT,
    "Dark Yellow": RIGHT,
    "Purple": RIGHT
}

# Color cycle list
COLOR_CYCLE = [
    WHITE,
    RED,
    GREEN,
    CYAN,
    YELLOW,
    PINK,
    GRAY,
    DARK_RED,
    DARK_GREEN,
    DARK_BLUE,
    DARK_YELLOW,
    PURPLE,
]

class Ant:
    def __init__(self, pos: Vector2, rows: int, cols: int) -> None:
        self.pos = pos
        self.direction = Directions.North
        self.gridRows = rows
        self.gridCols = cols

    def move(self, x: int, y: int) -> None:
        self.pos.x = (self.pos.x + x) % self.gridCols
        self.pos.y = (self.pos.y + y) % self.gridRows

    def goRight(self) -> None:
        if self.direction == Directions.North:
            self.direction = Directions.East
            self.move(1, 0)
        elif self.direction == Directions.East:
            self.direction = Directions.South
            self.move(0, 1)
        elif self.direction == Directions.South:
            self.direction = Directions.West
            self.move(-1, 0)
        else:
            self.direction = Directions.North
            self.move(0, -1)

    def goLeft(self) -> None:
        if self.direction == Directions.North:
            self.direction = Directions.West
            self.move(-1, 0)
        elif self.direction == Directions.West:
            self.direction = Directions.South
            self.move(0, 1)
        elif self.direction == Directions.South:
            self.direction = Directions.East
            self.move(1, 0)
        else:
            self.direction = Directions.North
            self.move(0, -1)

class Grid:
    def __init__(self, startColor: tuple=WHITE) -> None:
        self.cols = floor(WIDTH / CELL_SCALE)
        self.rows = floor(HEIGHT / CELL_SCALE)
        self.ant = Ant(Vector2(self.cols/2, self.rows/2), self.rows, self.cols)

        # Initialize grid list
        self.grid: list[list[tuple]] = []
        for y in range(self.rows):
            line: list[tuple] = []
            for x in range(self.cols):
                line.append(startColor)
            self.grid.append(line)

        # Draw grid once
        self.drawGrid()

    def moveAnt(self) -> None:
        x = floor(self.ant.pos.x)
        y = floor(self.ant.pos.y)

        # Get this cell's color value (RGB) and position on color cycle
        cellColor = self.grid[y][x]
        colorCycleIdx = COLOR_CYCLE.index(cellColor)

        # Get new color
        newColor = COLOR_CYCLE[(colorCycleIdx + 1) % len(COLOR_CYCLE)]
        colorName = list(COLORS.keys())[list(COLORS.values()).index(newColor)]

        # Update grid color
        self.paintCell(x, y, newColor)

        # Move ant
        if RULES[colorName] == LEFT:
            self.ant.goLeft()
        else:
            self.ant.goRight()

    def drawLines(self, surface: pygame.Surface=window) -> None:
        for x in range(self.cols + 1):
            pygame.draw.line(surface, LINE_COLOR, (x * CELL_SCALE + WORLD_OFFSET.x, 0), (x * CELL_SCALE + WORLD_OFFSET.x, HEIGHT))

        for y in range(self.rows + 1):
            pygame.draw.line(surface, LINE_COLOR, (0, y * CELL_SCALE + WORLD_OFFSET.y), (WIDTH, y * CELL_SCALE + WORLD_OFFSET.y))

    def drawGrid(self, surface: pygame.Surface=window) -> None:
        surface.fill(WHITE)
        for y in range(self.rows):
            for x in range(self.cols):
                self.drawCell(x, y, surface)

    def drawCell(self, x: int, y: int, surface: pygame.Surface=window) -> None:
        posX = x * CELL_SCALE + WORLD_OFFSET.x
        posY = y * CELL_SCALE + WORLD_OFFSET.y
        pygame.draw.rect(surface, self.grid[y][x], (posX, posY, CELL_SCALE, CELL_SCALE))

    def paintCell(self, x: int, y: int, color: tuple=None) -> None:
        self.grid[y][x] = color or choice(list(COLORS))
        self.drawCell(x, y)

    def paintRandom(self, color: tuple=None) -> None:
        x = randrange(0, self.cols)
        y = randrange(0, self.rows)
        self.grid[y][x] = color or choice(list(COLORS))

        self.drawCell(x, y)

WORLD_OFFSET = Vector2(0, 0)
GRID = Grid()
mouseDown = False
fDown = False
cont = False
incremental = 1
steps = 0

while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_f:
                fDown = True
            elif event.key == K_c:
                cont = not cont
            elif event.key == K_g:
                GRID.moveAnt()
            elif event.key == K_q:
                incremental = max(1, incremental/10)
            elif event.key == K_e:
                incremental *= 10
        elif event.type == KEYUP:
            if event.key == K_f:
                fDown = False
        # elif event.type == MOUSEMOTION and mouseDown:
        #     WORLD_OFFSET += Vector2(event.rel[0], event.rel[1])

    # Get mouse buttons state
    left, middle, right = pygame.mouse.get_pressed(3)
    mouseDown = left

    if fDown or cont:
        for i in range(floor(incremental)):
            GRID.moveAnt()
            steps += 1

    # GRID.drawGrid()
    # GRID.drawLines()

    pygame.display.set_caption(f"Langton Ant | Incremental: {incremental:.0f} | Steps: {steps:,} | FPS: {clock.get_fps():.0f}")
    pygame.display.update()
    clock.tick(FPS)