import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from random import randint
from math import atan2, floor, inf
from time import time
import os.path

pathFile = os.path.dirname(__file__)

pygame.init()
WIDTH = 1300
HEIGHT = 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 127, 0)

# Constants
CELL_SIZE = 15
SNAKE_MOVE_TIME = .01
COLS = floor(WIDTH / CELL_SIZE)
ROWS = floor(HEIGHT / CELL_SIZE)
LINE_WIDTH = 1
OFFSCREEN_CELLS_FRUIT_SPAWN = 25
INITIAL_FRUITS = 1500
WORLD_OFFSET = Vector2(0, 0)
ARROW_SIZE = Vector2(80, 40)
ARROW_DISTANCE_TO_SNAKE = 40

# Colors
BACKGROUND_COLOR = (130, 130, 130)
SNAKE_COLOR = GREEN
FRUIT_COLOR = RED
LINE_COLOR = (30, 30, 30)

# States
mouseDown = False
cameraLocked = False
followButtonDown = False

# Sprites
arrowSprite = pygame.transform.scale(pygame.image.load(os.path.join(pathFile, "images/arrow1.png")).convert_alpha(), (ARROW_SIZE.x, ARROW_SIZE.y))

# Function to convert world offset into grid offset
def worldToGrid() -> Vector2:
    return Vector2(WORLD_OFFSET.x // CELL_SIZE * CELL_SIZE,
                   WORLD_OFFSET.y // CELL_SIZE * CELL_SIZE)

# Function to add a fruit randomly on the grid
def addFruit(pos: Vector2=None) -> None:
    if pos != None:
        print("Added fruit")
        fruits.append(Fruit(pos))
        return

    # Get offset and position constraints
    offset = worldToGrid()
    minX = -offset.x / CELL_SIZE        - OFFSCREEN_CELLS_FRUIT_SPAWN
    maxX = -offset.x / CELL_SIZE + COLS + OFFSCREEN_CELLS_FRUIT_SPAWN
    minY = -offset.y / CELL_SIZE        - OFFSCREEN_CELLS_FRUIT_SPAWN
    maxY = -offset.y / CELL_SIZE + ROWS + OFFSCREEN_CELLS_FRUIT_SPAWN

    while True:
        # Get random position
        x = randint(floor(minX), floor(maxX))
        y = randint(floor(minY), floor(maxY))

        # Check if there is no snake in the chosen cell
        valid = True
        for snake in snakes:
            for segment in snake.getBody():
                if segment.x == x and segment.y == y:
                    valid = False
                    break
            
            if not valid:
                break

        # Check for fruits as well
        for fruit in fruits:
            if fruit.pos.x == x and fruit.pos.y == y and valid:
                valid = False
                break

        # If it's valid, add a fruit
        if valid:
            print(f"Added fruit on pos ({x}, {y})")
            fruits.append(Fruit(Vector2(x, y)))
            break

# Function to draw grid
def drawGrid() -> None:
    for x in range(COLS):
        pygame.draw.line(window, LINE_COLOR, (x * CELL_SIZE, 0),
                                             (x * CELL_SIZE, HEIGHT), LINE_WIDTH)

    for y in range(ROWS):
        pygame.draw.line(window, LINE_COLOR, (0,     y * CELL_SIZE),
                                             (WIDTH, y * CELL_SIZE), LINE_WIDTH)

# Function to show game over screen
def gameOver() -> None:
    pass

# Function to focus "camera" on snake
def focusSnake() -> None:
    snakeHead = snakes[0].getBody()[0]
    WORLD_OFFSET.x = (-snakeHead.x + COLS/2) * CELL_SIZE
    WORLD_OFFSET.y = (-snakeHead.y + ROWS/2) * CELL_SIZE

# Function to show an arrow pointing to the closest offscreen fruit
def arrowToFruit() -> None:
    offscreenFruits: list[Fruit] = []
    offset = worldToGrid()

    for fruit in fruits:
        if ((fruit.pos.x >= offset.x and fruit.pos.x < offset.x + COLS) and
            (fruit.pos.y >= offset.y and fruit.pos.y < offset.y + ROWS)):
            # We have at least one fruit on screen, so no need to blit arrow
            print(f"At least one onScreen fruit at pos ({fruit.pos.x}, {fruit.pos.y})")
            return
        else:
            # This fruit is offscreen, so add to the list
            offscreenFruits.append(fruit)

    # Get the closest fruit
    minDist = inf
    closestFruit: Fruit = None
    snakeHead = snakes[0].getBody()[0]
    for fruit in offscreenFruits:
        dist = fruit.pos.distance_squared_to(snakeHead)
        if dist < minDist:
            minDist = dist
            closestFruit = fruit

    direction = (closestFruit.pos - snakeHead).normalize()
    angle = atan2(direction.y, direction.x)
    # print(angle)

    sprite = pygame.transform.rotate(arrowSprite, angle)
    spritePos = (snakeHead) * CELL_SIZE - ARROW_SIZE/2 + Vector2(CELL_SIZE, CELL_SIZE)/2# + direction * ARROW_DISTANCE_TO_SNAKE
    print(spritePos)
    # print(f"Drawing arrow at {spritePos}")
    window.blit(sprite, spritePos)

class Direction:
    Up = Vector2(0, -1)
    Down = Vector2(0, 1)
    Left = Vector2(-1, 0)
    Right = Vector2(1, 0)

class Fruit:
    def __init__(self, pos: Vector2, color: tuple=None) -> None:
        self.pos = pos
        self.color = color or FRUIT_COLOR
    
    def draw(self) -> None:
        offset = worldToGrid()
        pygame.draw.rect(window, self.color, (self.pos.x * CELL_SIZE + offset.x,
                                              self.pos.y * CELL_SIZE + offset.y, CELL_SIZE, CELL_SIZE))

class Snake:
    def __init__(self, startPos: Vector2=None, startLength: int=4, color: tuple=None) -> None:
        self.color = color or SNAKE_COLOR
        self.startPos = startPos or Vector2(WIDTH/CELL_SIZE/2, HEIGHT/CELL_SIZE/2)
        self.startLength = startLength
        self.direction = Direction.Right
        self.__lastMove = time()
        self.createBody()

        # To prevent changing direction more than once before moving again, create a debounce
        self.__directionDebouce = False

    def getBody(self) -> list[Vector2]:
        return self.__body[:]

    def createBody(self) -> None:
        # Clear body
        self.__body: list[Vector2] = []

        # Reset direction
        self.direction = Direction.Right

        # Add segments
        for i in range(self.startLength):
            self.__body.append(self.startPos - self.direction * i)

    def move(self) -> None:
        if not time() > self.__lastMove + SNAKE_MOVE_TIME:
            return
        self.__lastMove = time()

        # Get current and next head position
        headPos = self.__body[0]
        nextPos = headPos + self.direction
        # Add new segment at index 0
        self.__body.insert(0, nextPos)

        # Check if snake ate a fruit
        ateFruit = False
        for fruit in fruits:
            if fruit.pos.x == nextPos.x and fruit.pos.y == nextPos.y:
                ateFruit = True
                fruits.remove(fruit)
                addFruit()
                break

        if not ateFruit:
            # Remove tail
            self.__body.pop()

        # Change direction debounce
        self.__directionDebouce = False

        # Check if is dead
        if self.isDead():
            # gameOver()

            # Restart snake
            self.createBody()

    def changeDirection(self, newDirection: Vector2) -> None:
        if newDirection != self.direction and newDirection != -self.direction and not self.__directionDebouce:
            self.__directionDebouce = True
            self.direction = newDirection

    def isDead(self) -> bool:
        head = self.__body[0]
        for segment in self.__body[1:]:
            if segment.x == head.x and segment.y == head.y:
                return True

        return False

    def draw(self) -> None:
        for segmentPos in self.__body:
            offset = worldToGrid()
            x = CELL_SIZE * floor(segmentPos.x) + offset.x
            y = CELL_SIZE * floor(segmentPos.y) + offset.y

            pygame.draw.rect(window, self.color, (x, y, CELL_SIZE, CELL_SIZE))

# Lists of snakes and fruits
snakes: list[Snake] = []
fruits: list[Fruit] = []

# Create a snake
snake = Snake(startLength=150)
snakes.append(snake)

# Add random fruits
for i in range(INITIAL_FRUITS):
    addFruit()

while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in (K_w, K_UP):
                snake.changeDirection(Direction.Up)
            elif event.key in (K_a, K_LEFT):
                snake.changeDirection(Direction.Left)
            elif event.key in (K_s, K_DOWN):
                snake.changeDirection(Direction.Down)
            elif event.key in (K_d, K_RIGHT):
                snake.changeDirection(Direction.Right)
            elif event.key == K_f:
                head = snakes[0].getBody()[0]
                offset = worldToGrid()
                print(f"Snake Head Pos: ({head.x:.0f}, {head.y:.0f})\nWorld Offset: ({offset.x:.0f}, {offset.y:.0f})")
            elif event.key == K_y:
                cameraLocked = not cameraLocked
            elif event.key == K_SPACE:
                followButtonDown = True
        elif event.type == KEYUP:
            if event.key == K_SPACE:
                followButtonDown = False
        elif event.type == MOUSEMOTION and mouseDown:
            WORLD_OFFSET += Vector2(event.rel[0], event.rel[1])

    # Get mouse buttons state
    left, middle, right = pygame.mouse.get_pressed(3)
    mouseDown = left

    window.fill(BACKGROUND_COLOR)

    for fruit in fruits:
        fruit.draw()

    # Move all snakes
    for snake in snakes:
        snake.move()

    if cameraLocked or followButtonDown:
        # Focus "camera" on snake
        focusSnake()

    # Draw snakes
    for snake in snakes:
        snake.draw()

    # Draw grid lines
    drawGrid()

    # Draw arrow towards fruit
    # arrowToFruit()

    pygame.display.set_caption(f"Snake | FPS: {clock.get_fps():.0f}")
    pygame.display.update()
    clock.tick(FPS)

'''
DONE:
 - Desenhar as linhas corretamente de acordo com o WORLD_OFFSET
 - Quando o usuário apertar um botão (espaço, Y ou sla), focar a "câmera" na cobra

TODO:
 - Se não tiver nenhum fruta no campo de visão, colocar uma seta na tela apontando para a fruta mais próxima
 - Adicionar texturas pra cobra (cabeça e corpo), fruta e... chão?
 - Adicionar menu com controles e etc
 PASSAR TUDO PRO MICKAELREI

'''