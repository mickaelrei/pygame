from math import floor
import pygame
from pygame.locals import *
from pygame.math import Vector2
import sys
from random import random, randint, choice
from solver import Solver
import paintings

WIDTH = 600
HEIGHT = 600
FPS = 600
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

def drawText(text: str, pos: Vector2, fontSize: int=18, fontType: str="comicsans", bold: bool=False,
             italic: bool=False, antiAlias: bool=False, textColor: tuple=BLACK, bgColor: tuple=None,
             anchorX: float=0, anchorY: float=0, surface: pygame.Surface=window):
    font = pygame.font.SysFont(fontType, round(fontSize), bold, italic)
    textSurface = font.render(str(text), antiAlias, textColor, bgColor)
    textRect = textSurface.get_rect()
    surfPos = [pos.x + textRect.width * anchorX, pos.y + textRect.height * anchorY]
    surface.blit(textSurface, surfPos)
    return surface, surfPos

def map(n, start1, stop1, start2, stop2):
  return (n - start1) / (stop1 - start1) * (stop2 - start2) + start2

def getDictKeyFromVal(d: dict, val):
    for key, value in d.items():
        if val == value:
            return key
 
    raise KeyError(f"Value {val} not found in dict")

def endGame(won: bool=False):
    # Draw board one last time
    window.fill(WHITE)
    board.draw()

    # Draw menu background
    endMenuBottomPadding = 10
    endMenuSize = Vector2(250, 100)
    endMenuBackgroundColor = (150, 150, 150)
    pygame.draw.rect(window, endMenuBackgroundColor, (WIDTH/2 - endMenuSize.x/2, HEIGHT - endMenuSize.y - endMenuBottomPadding, endMenuSize.x, endMenuSize.y))

    # Draw text
    text = "You lost!"
    if won:
        text = "You won!"

    # Draw black border and white text
    drawText(text, Vector2(WIDTH/2, HEIGHT - endMenuSize.y/2 - endMenuBottomPadding), fontSize=40, bold=True, anchorX=-.5, anchorY=-.5, textColor=BLACK)


    # Update screen and wait for input to close game
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

def handleClick():
    global currentLife

    # Check if mouse is inside board
    if not (mousePos.x > BOARD_TOPLEFT.x and mousePos.x < BOARD_BOTTOMRIGHT.x and mousePos.y > BOARD_TOPLEFT.y and mousePos.y < BOARD_BOTTOMRIGHT.y):
        # Check if mouse is inside any selector
        for selector in board.selectors:
            if selector.pos.distance_to(mousePos) <= selector.radius:
                board.changeSelector(selector.color, selector.isX)

        return

    # Get cell for mouse position
    col = floor(map(mousePos.x, BOARD_TOPLEFT.x, BOARD_BOTTOMRIGHT.x, 0, COLS))
    row = floor(map(mousePos.y, BOARD_TOPLEFT.y, BOARD_BOTTOMRIGHT.y, 0, ROWS))
    board.revealCell(col=col, row=row)

class Digit:
    def __init__(self, color: pygame.Color=BLACK, count: int=1) -> None:
        self.color = color
        self.count = count

    def __repr__(self) -> str:
        return f"{getDictKeyFromVal(DEFAULT_COLOR_MAP, self.color)}{self.count}"

class Cell:
    def __init__(self, isX: bool=False, color: pygame.Color=BLACK, revealed: bool=False) -> None:
        self.isX = isX
        self.color = color
        self.revealed = revealed

    def __repr__(self) -> str:
        if self.isX:
            return "X"
        return f"{getDictKeyFromVal(DEFAULT_COLOR_MAP, self.color)}"

class Selector:
    def __init__(self, pos: Vector2, isX: bool, color: tuple=BLACK, radius: float=15, selected: bool=False) -> None:
        self.color = color
        self.pos = pos
        self.radius = radius
        self.selected = selected
        self.isX = isX

    def checkClick(self) -> None:
        pass

    def draw(self, surface: pygame.Surface=window) -> None:
        # Draw background circle
        color = SELECTOR_BACKGROUND_COLOR
        if self.selected:
            color = SELECTOR_SELECTED_BACKGROUND_COLOR
        pygame.draw.circle(surface, color, self.pos, self.radius)

        # If this is the X selector, draw an X
        if self.isX:
            paddingX = 2
            pygame.draw.line(surface, CELL_X_COLOR,
                (self.pos.x - self.radius/2 + paddingX, self.pos.y - self.radius/2 + paddingX),
                (self.pos.x + self.radius/2 - paddingX, self.pos.y + self.radius/2 - paddingX),
            CELL_X_WIDTH)
            pygame.draw.line(surface, CELL_X_COLOR, 
                (self.pos.x + self.radius/2 - paddingX, self.pos.y - self.radius/2 + paddingX),
                (self.pos.x - self.radius/2 + paddingX, self.pos.y + self.radius/2 - paddingX),
            CELL_X_WIDTH)
        # Else, draw rect for selector color
        else:
            pygame.draw.rect(surface, self.color, (
                self.pos.x - self.radius/2, self.pos.y - self.radius/2,
                self.radius, self.radius
            ))

class Board:
    def __init__(self, rows: int=10, cols: int=10) -> None:
        self.cols = cols
        self.rows = rows
        self.colorMap = DEFAULT_COLOR_MAP
        self.selectors: list[Selector] = []

        sizeX = (WIDTH - BOARD_TOPLEFT.x - (WIDTH - BOARD_BOTTOMRIGHT.x)) / cols
        sizeY = (HEIGHT - BOARD_TOPLEFT.y - (HEIGHT - BOARD_BOTTOMRIGHT.y)) / rows 
        self.cellSize = Vector2(sizeX, sizeY)
        self.board: list[list[Cell]] = []
        for i in range(rows):
            line: list[Cell] = []
            for j in range(cols):
                color = choice(list(self.colorMap.values()))
                cell = Cell(random() > .7, color, False)
                line.append(cell)
            self.board.append(line)

    def changeSelector(self, color: tuple=None, isX: bool=False) -> None:
        # Change selected attribute on previous and current selector
        self.currentSelector.selected = False
        if isX:
            self.currentSelector = self.selectors[0]
        else:
            for selector in self.selectors:
                if selector.color == color:
                    self.currentSelector = selector
                
        self.currentSelector.selected = True

    def createDigits(self) -> None:
        rowsDigits: list[list[Digit]] = []
        colsDigits: list[list[Digit]] = []

        # Get rows
        for row in range(self.rows):
            lastColor = None
            lastCount = 0
            rowDigits = []
            for i in range(self.cols):
                cell = self.board[row][i]
                if lastColor == None and not cell.isX:
                    lastColor = cell.color
                    lastCount = 0

                if not cell.isX and cell.color == lastColor:
                    lastCount += 1
                elif lastColor:
                    # Add new digit
                    rowDigits.append(Digit(lastColor, lastCount))
                    lastCount = 1
                    if cell.isX:
                        lastColor = None
                    else:
                        lastColor = cell.color

            # Add last if needed
            if lastColor and lastCount > 0:
                rowDigits.append(Digit(lastColor, lastCount))
            # Invert row list
            for i, digit in enumerate(rowDigits[:]):
                rowDigits[len(rowDigits) - 1 - i] = digit
            rowsDigits.append(rowDigits)
        
        self.rowsDigits = rowsDigits

        # Get cols
        for col in range(self.cols):
            # Get all cells for this column
            cells: list[Cell] = []
            for i in range(self.rows):
                cells.append(self.board[i][col])

            lastColor = None
            lastCount = 0
            colDigits = []
            for cell in cells:
                if lastColor == None and not cell.isX:
                    lastColor = cell.color
                    lastCount = 0

                if not cell.isX and cell.color == lastColor:
                    lastCount += 1
                elif lastColor:
                    # Add new digit
                    colDigits.append(Digit(lastColor, lastCount))
                    lastCount = 1
                    if cell.isX:
                        lastColor = None
                    else:
                        lastColor = cell.color

            # Add last if needed
            if lastColor and lastCount > 0:
                colDigits.append(Digit(lastColor, lastCount))
            # Invert col list
            for i, digit in enumerate(colDigits[:]):
                colDigits[len(colDigits) - 1 - i] = digit
            colsDigits.append(colDigits)

        self.colsDigits = colsDigits

    def createSelectors(self) -> None:
        # Number of color selectors (+1 for the X selector)
        c = len(self.colorMap.values()) + 1

        # Calculate Y position and padding
        centerX = BOARD_TOPLEFT.x + (BOARD_BOTTOMRIGHT.x - BOARD_TOPLEFT.x)/2
        y = BOARD_BOTTOMRIGHT.y + SELECTORS_MENU_SIZE/2
        if c % 2 == 0:
            left = centerX - BOARD_PADDING/4 - SELECTOR_RADIUS * (c - 1) - SELECTOR_PADDING * (c - 2)/2
        else:
            left = centerX - SELECTOR_RADIUS * (c - 1) - SELECTOR_PADDING * (c - 1)/2
        i = 1
        for name, color in self.colorMap.items():
            x = left + SELECTOR_PADDING * i + SELECTOR_RADIUS * i * 2
            selector = Selector(Vector2(x, y), False, color, SELECTOR_RADIUS, i == 1)
            self.selectors.append(selector)

            i += 1

        # Add X selector
        selectorX = Selector(Vector2(left, y), True, radius=SELECTOR_RADIUS, selected=False)
        self.selectors.insert(0, selectorX)

        self.currentSelector = self.selectors[1]

    @staticmethod
    def fromTemplate(template: dict):
        boardList = template['board']
        board: Board = Board(rows=len(boardList), cols=len(boardList[0]))
        board.colorMap: dict = template['colorMap']
        for i in range(board.rows):
            for j in range(board.cols):
                s = boardList[i][j]
                cell = Cell(s == ".", board.colorMap.get(s) or BLACK, REVEAL_BOARD)
                board.board[i][j] = cell

        return board

    def checkRowCompletion(self, row: int=0) -> None:
        completed = True
        for i in range(self.cols):
            cell = self.board[row][i]
            if not (cell.revealed or cell.isX):
                completed = False
                break
        if completed:
            for i in range(self.cols):
                self.board[row][i].revealed = True

    def checkColCompletion(self, col: int=0) -> None:
        completed = True
        for i in range(self.rows):
            cell = self.board[i][col]
            if not (cell.revealed or cell.isX):
                completed = False
                break
        if completed:
            for i in range(self.rows):
                self.board[i][col].revealed = True

    def revealCell(self, row: int=0, col: int=0) -> None:
        global currentLife
        cell: Cell = self.board[row][col]
        if cell.revealed: return

        if (cell.isX and self.currentSelector.isX) or (not cell.isX and cell.color == self.currentSelector.color):
            # Got right
            pass
        else:
            currentLife -= 1
            if currentLife == 0:
                endGame()

        # Reveal cell
        cell.revealed = True

        # Check if row is completed
        self.checkRowCompletion(row)

        # Check if col is completed
        self.checkColCompletion(col)

        # Check if board done
        self.checkDone()

    def checkDone(self) -> bool:
        done = True
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.board[row][col]
                if not cell.isX and not cell.revealed:
                    done = False
                    break
            if not done: break
        if done:
            endGame(won=True)

    def draw(self, surface: pygame.Surface=window):
        # Draw cells
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.board[i][j]

                # Find top-left and bottom-right points
                x = BOARD_TOPLEFT.x + self.cellSize.x * j
                y = BOARD_TOPLEFT.y + self.cellSize.y * i
                if cell.revealed:
                    if cell.isX:
                        # Draw X
                        pygame.draw.line(surface, CELL_X_COLOR, (x + CELL_X_PADDING, y + CELL_X_PADDING), (x + self.cellSize.x - CELL_X_PADDING, y + self.cellSize.y - CELL_X_PADDING), CELL_X_WIDTH)
                        pygame.draw.line(surface, CELL_X_COLOR, (x + self.cellSize.x - CELL_X_PADDING, y + CELL_X_PADDING), (x + CELL_X_PADDING, y + self.cellSize.y - CELL_X_PADDING), CELL_X_WIDTH)
                    else:
                        # Draw square with color
                        pygame.draw.rect(surface, cell.color, (x, y, self.cellSize.x, self.cellSize.y))
        
        # Draw inner lines
        for i in range(1, self.cols):
            x = map(i, 0, self.cols, BOARD_TOPLEFT.x, BOARD_BOTTOMRIGHT.x)
            color = INNERLINE_COLOR
            width = INNERLINE_WIDTH
            if i % 5 == 0:
                color = BORDER_COLOR
                width *= 2
            pygame.draw.line(surface, color, (x, BOARD_TOPLEFT.y), (x, BOARD_BOTTOMRIGHT.y), width)

        for i in range(1, self.rows):
            y = map(i, 0, self.rows, BOARD_TOPLEFT.y, BOARD_BOTTOMRIGHT.y)
            color = INNERLINE_COLOR
            width = INNERLINE_WIDTH
            if i % 5 == 0:
                color = BORDER_COLOR
                width *= 2
            pygame.draw.line(surface, color, (BOARD_TOPLEFT.x, y), (BOARD_BOTTOMRIGHT.x, y), width)

        # Draw digits
        for row in range(self.rows):
            # Digits nav position
            x = BOARD_TOPLEFT.x - DIGITS_NAV_SIZE
            y = BOARD_TOPLEFT.y + self.cellSize.y * row

            # Background
            pygame.draw.rect(window, DIGITS_BACKGROUND_COLOR, (x + DIGITS_NAV_BORDER_WIDTH, y + DIGITS_NAV_BORDER_WIDTH, DIGITS_NAV_SIZE - DIGITS_NAV_BORDER_WIDTH*2, self.cellSize.y - DIGITS_NAV_BORDER_WIDTH*2))

            # Digits
            digits = self.rowsDigits[row]
            if len(digits) == 0:
                # Draw border and continue to next
                pygame.draw.rect(window, DIGITS_BORDER_COLOR, (x, y, DIGITS_NAV_SIZE, self.cellSize.y), BORDER_WIDTH)
                continue

            # Get size and pos
            digitSize = min(MAX_DIGIT_SIZE, (DIGITS_NAV_SIZE - BORDER_WIDTH * 1.5) / len(digits))
            for i, digit in enumerate(digits):
                digitX = x + DIGITS_NAV_SIZE - BORDER_WIDTH - digitSize * (i + 1)
                pygame.draw.rect(window, digit.color, (digitX + BORDER_WIDTH, y + BORDER_WIDTH, digitSize - BORDER_WIDTH, self.cellSize.y - BORDER_WIDTH*2), border_radius=5)
                textColor = (digit.color[0] * .299 + digit.color[1] * .587 + digit.color[2] * .114) > 150 and BLACK or WHITE
                drawText(digit.count, Vector2(digitX + BORDER_WIDTH + (digitSize-BORDER_WIDTH)/2, y + BORDER_WIDTH + (self.cellSize.y-BORDER_WIDTH*2)/2), textColor=textColor, anchorX=-.5, anchorY=-.5, fontSize=min(self.cellSize.y, digitSize)/1.6, bold=True)

            # Border
            pygame.draw.rect(window, DIGITS_BORDER_COLOR, (x, y, DIGITS_NAV_SIZE, self.cellSize.y), BORDER_WIDTH)

        for col in range(self.cols):
            # Digits nav position
            x = BOARD_TOPLEFT.x + self.cellSize.x * col
            y = BOARD_TOPLEFT.y - DIGITS_NAV_SIZE

            # Background
            pygame.draw.rect(window, DIGITS_BACKGROUND_COLOR, (x + DIGITS_NAV_BORDER_WIDTH, y + DIGITS_NAV_BORDER_WIDTH, self.cellSize.x - DIGITS_NAV_BORDER_WIDTH*2, DIGITS_NAV_SIZE - DIGITS_NAV_BORDER_WIDTH*2))

            # Digits
            digits = self.colsDigits[col]
            if len(digits) == 0:
                # Draw border and continue to next
                pygame.draw.rect(window, DIGITS_BORDER_COLOR, (x, y, self.cellSize.x, DIGITS_NAV_SIZE), BORDER_WIDTH)
                continue

            # Get size and pos
            digitSize = min(MAX_DIGIT_SIZE, (DIGITS_NAV_SIZE - BORDER_WIDTH * 1.5) / len(digits))
            for i, digit in enumerate(digits):
                digitY = y + DIGITS_NAV_SIZE - BORDER_WIDTH - digitSize * (i + 1)
                pygame.draw.rect(window, digit.color, (x + BORDER_WIDTH, digitY + BORDER_WIDTH, self.cellSize.x - BORDER_WIDTH*2, digitSize - BORDER_WIDTH), border_radius=5)
                textColor = (digit.color[0] * .299 + digit.color[1] * .587 + digit.color[2] * .114) > 150 and BLACK or WHITE
                drawText(digit.count, Vector2(x + BORDER_WIDTH + (self.cellSize.x-BORDER_WIDTH)/2, digitY + BORDER_WIDTH + (digitSize-BORDER_WIDTH*2)/2), textColor=textColor, anchorX=-.5, anchorY=-.5, fontSize=min(self.cellSize.x, digitSize)/1.6, bold=True)

            # Border
            pygame.draw.rect(window, DIGITS_BORDER_COLOR, (x, y, self.cellSize.x, DIGITS_NAV_SIZE), BORDER_WIDTH)

        # Draw selectors
        for selector in self.selectors:
            selector.draw()

        # Draw borders
        pygame.draw.line(surface, BORDER_COLOR, BOARD_TOPLEFT, (BOARD_BOTTOMRIGHT.x, BOARD_TOPLEFT.y), BORDER_WIDTH)
        pygame.draw.line(surface, BORDER_COLOR, (BOARD_BOTTOMRIGHT.x, BOARD_TOPLEFT.y), BOARD_BOTTOMRIGHT, BORDER_WIDTH)
        pygame.draw.line(surface, BORDER_COLOR, BOARD_BOTTOMRIGHT, (BOARD_TOPLEFT.x, BOARD_BOTTOMRIGHT.y), BORDER_WIDTH)
        pygame.draw.line(surface, BORDER_COLOR, (BOARD_TOPLEFT.x, BOARD_BOTTOMRIGHT.y), BOARD_TOPLEFT, BORDER_WIDTH)

# Constants
ROWS = 10
COLS = 10
MAX_LIFE = 3
REVEAL_BOARD = False
BOARD_PADDING = 50
BOARD_TOPLEFT = Vector2(100, 100)
BOARD_BOTTOMRIGHT = Vector2(WIDTH - 100, HEIGHT - 100)
DIGITS_NAV_SIZE = 75
MAX_DIGIT_SIZE = 25
SELECTORS_MENU_SIZE = 50
SELECTOR_RADIUS = 15
SELECTOR_PADDING = 25
DIGITS_NAV_BORDER_WIDTH = 3
BORDER_WIDTH = 3
INNERLINE_WIDTH = 1
CELL_X_WIDTH = 5
CELL_X_PADDING = 10
SELECTOR_BACKGROUND_COLOR = WHITE #(150, 150, 150)
SELECTOR_SELECTED_BACKGROUND_COLOR = (170, 170, 170)
BORDER_COLOR = (80, 80, 80)
INNERLINE_COLOR = (150, 150, 150)
CELL_X_COLOR = (100, 100, 100)
DIGITS_BACKGROUND_COLOR = (180, 180, 180)
DIGITS_BORDER_COLOR = (90, 90, 90)
DEFAULT_COLOR_MAP = {
    "g": GREEN,
    "r": RED,
    "B": BLUE,
    "b": BLACK,
    "y": YELLOW,
}

# Variables
currentLife = MAX_LIFE
chosenBoard = paintings.amogus
board = Board.fromTemplate(chosenBoard)
# board = Board(rows=ROWS, cols=COLS)
board.createDigits()
board.createSelectors()

# Create solver
solver = Solver(board)

# Check all rows and cols completions
for row in range(ROWS):
    board.checkRowCompletion(row)

for col in range(COLS):
    board.checkColCompletion(col)
     
while True:
    mousePos = Vector2(pygame.mouse.get_pos())
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    # Handle mouse click
    leftDown, _, rightDown = pygame.mouse.get_pressed()
    if leftDown:
        handleClick()

    window.fill(WHITE)

    # Next try of solver
    solver.next()

    # Check if solver finished
    if solver.finished:
        # Check if board is completed
        pass

    # Draw board
    board.draw()

    # Show current life
    drawText(f"Current life: {currentLife} ", pos=Vector2(10, HEIGHT - 5), anchorY=-1, textColor=RED, bold=True, fontType="courier new")
    
    pygame.display.set_caption(f"Nonogram | FPS: {clock.get_fps():.0f}")
    pygame.display.update()
    clock.tick(FPS)