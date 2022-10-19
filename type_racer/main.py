import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from math import inf, cos, pi, radians, sin, atan, atan2
from random import randint, random
from time import time
import os.path

pygame.init()
WIDTH = 500
HEIGHT = 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 127, 0)
YELLOW = (255, 0, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (127, 0, 255)
COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]  

def drawText(text: str, pos: Vector2, fontSize: int=18, fontType: str="comicsans", bold: bool=False,
             italic: bool=False, antiAlias: bool=False, textColor: tuple=BLACK, bgColor: tuple=None,
             centerX: float=0, centerY: float=0, surface: pygame.Surface=window) -> Vector2:
    font = pygame.font.SysFont(fontType, fontSize, bold, italic)
    textSurface = font.render(text, antiAlias, textColor, bgColor)
    textRect = textSurface.get_rect()
    surface.blit(textSurface, [pos.x + (textRect.width/2) * centerX, pos.y + (textRect.height/2) * centerY])

class Word:
    def __init__(self, pos: Vector2, word: str, direction: Vector2, speed: float) -> None:
        self.pos = pos
        self.word = word
        self.typed = ""
        self.direction = direction if direction.length_squared() == 1 else direction.normalize()
        self.speed = speed

        # Get text rect size
        font = pygame.font.SysFont(FONT_TYPE, FONT_SIZE, False, False)
        textSurface = font.render(self.word, False, WHITE, BLACK)
        textRect = textSurface.get_rect()

        # Set size
        self.size = Vector2(textRect.width, textRect.height)        

    def update(self) -> None:
        global currentWord

        self.pos += self.direction * self.speed

        if self.pos.x + self.size.x/2 > WIDTH or self.pos.x - self.size.x/2 < 0:
            self.direction.x *= -1
        
        if self.pos.y > HEIGHT:
            if currentWord == self:
                currentWord = None
            currentWords.remove(self)
            generateWord()
            return

    def draw(self) -> None:
        # Draw typed text in orange
        text = " " * len(self.typed) + self.word[len(self.typed):]

        # Draw
        drawText(text.upper(), fontType="courier new", pos=self.pos, textColor=currentWord == self and ORANGE or WHITE, centerX=-1, centerY=-1)

def generateWord() -> None:
    pos = Vector2(randint(50, WIDTH-50), -15)
    direction = Vector2(randint(3, 10), randint(6, 10))
    currentWords.append(Word(pos, createWord(), direction, SPEED))

def createWord() -> str:
    while True:
        chosenWord = possibleWords[randint(0, len(possibleWords)-1)]
        
        if len(currentWords) == 0:
            break

        valid = True
        for word in currentWords:
            if word.word[0] == chosenWord[0]:
                valid = False
                break

        if valid:
            break
        
    return chosenWord

# Get words list
with open(os.path.join(__file__, "../words.txt")) as file:
    wordsList = file.readlines()
    file.close()

# Filter words list
minWordSize = 3
possibleWords: list[str] = []
for word in wordsList:
    word: str = word[:-1]
    if len(word) >= minWordSize and word.count("-") == 0:
        possibleWords.append(word.lower())

# Variables
SPEED = 1.3
FONT_TYPE = "courier new"
FONT_SIZE = 18
WORD_COLOR = WHITE
FOCUSED_WORD_COLOR = ORANGE
MAX_WORDS_ON_SCREEN = 6
NEW_WORD_DELAY = .6

alphabet = "abcdefghijklmnopqrstuvwxyz"
currentWord: Word = None
currentTyping = ""
lastWordTime = 0

# List of Word objects
currentWords: list[Word] = []

while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            keyName = pygame.key.name(event.key)

            # Find word that starts with this
            if currentWord is None:
                for word in currentWords:
                    if word.word.lower()[0] == keyName:
                        currentWord = word
                        currentTyping = keyName
                        currentWord.typed = keyName
                        break
            else:
                if currentWord.word[len(currentTyping)] == keyName:
                    currentWord.typed += keyName
                    currentTyping += keyName
                    if len(currentWord.typed) == len(currentWord.word):
                        currentWords.remove(currentWord)
                        currentTyping = ""
                        currentWord = None
                        # generateWord()

    window.fill(BLACK)

    # Check if need to add new word
    if time() > lastWordTime + NEW_WORD_DELAY and len(currentWords) < MAX_WORDS_ON_SCREEN:
        lastWordTime = time()
        generateWord()

    # if len(currentWords) == 0:
    #     pygame.quit()
    #     print("You won!")
    #     sys.exit()

    for word in currentWords:
        word.update()
        word.draw()

    pygame.display.update()
    clock.tick(FPS)

"""

TODO:
 - Pintar o texto escrito em roxo e o não escrito em branco
 - Fazer uma torre la embaixo que mira na palavar atual e atira quando ela termina
 - Fazer uma explosão qnd a palavra temina
 - Desenhar a palavra em "arco"
 - 


"""