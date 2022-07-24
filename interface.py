import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2
from random import randint
from math import cos, pi, sin, radians, inf

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

def drawText(text: str, pos: Vector2, fontSize: int=18, fontType: str="comicsans", bold: bool=False,
             italic: bool=False, antiAlias: bool=False, textColor: tuple=BLACK, bgColor: tuple=None,
             centerX: float=0, centerY: float=0, surface: pygame.Surface=window):
    font = pygame.font.SysFont(fontType, fontSize, bold, italic)
    textSurface = font.render(str(text), antiAlias, textColor, bgColor)
    textRect = textSurface.get_rect()
    surface.blit(textSurface, [pos.x + (textRect.width/2) * centerX, pos.y + (textRect.height/2) * centerY])

class Button:
    def __init__(self, pos: Vector2=None, width: int=50, height: int=50, color: tuple=BLACK,
                 backgroundTransparency: float=0, cornerRoundiness: float=0, text: str="") -> None:
        self.pos = pos or Vector2(0, 0)
        self.width = width
        self.height = height
        self.color = color
        self.backgroundTransparency = backgroundTransparency
        self.cornerRoundiness = cornerRoundiness
        self.text = text
        self.isHeld = False
        self.surface = pygame.Surface((self.width, self.height))

    def changeTransparency(self, transparency: float=0) -> None:
        self.backgroundTransparency = transparency
        self.surface.set_alpha(round((1 - self.backgroundTransparency) * 255))

    def checkClick(self) -> bool:
        if (not self.isHeld and leftButtonPressed and
           (mousePos.x > self.pos.x - self.width/2 or mousePos.x < self.pos.x + self.width/2) and 
           (mousePos.y > self.pos.y - self.height/2 or mousePos.y < self.pos.y + self.height/2)):
            self.isHeld = True
            return True
        else:
            return False

    def checkHold(self) -> bool:
        return leftButtonPressed and self.isHeld

    def checkRelease(self) -> bool:
        if not leftButtonPressed and self.isHeld:
            self.isHeld = False
            return True

        return False

    def draw(self, surface: pygame.Surface=window) -> None:
        # Set some variables
        rect = Rect(self.pos.x, self.pos.y, self.width, self.height)
        color = Color(*self.color)
        color.a = round((1 - self.backgroundTransparency) * 255)
        alpha = color.a
        color.a = 0
        rect.topleft = 0,0
        rectangle = pygame.Surface(rect.size,SRCALPHA)

        # Create circles surface
        circle = pygame.Surface([min(rect.size)*3]*2, SRCALPHA)
        pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
        circle = pygame.transform.smoothscale(circle, [int(min(rect.size)*self.cornerRoundiness)]*2)

        # Draw circles on each corner
        radius = rectangle.blit(circle, (0,0))
        radius.bottomright = rect.bottomright
        rectangle.blit(circle,radius)
        radius.topright = rect.topright
        rectangle.blit(circle,radius)
        radius.bottomleft = rect.bottomleft
        rectangle.blit(circle,radius)

        # Fill colors
        rectangle.fill(BLACK, rect.inflate(-radius.w,0))
        rectangle.fill(BLACK, rect.inflate(0,-radius.h))

        rectangle.fill(color, special_flags=BLEND_RGBA_MAX)
        rectangle.fill((255, 255, 255, alpha), special_flags=BLEND_RGBA_MIN)

        drawText(self.text, Vector2(self.width/2, self.height/2), surface=rectangle, centerX=-1, centerY=-1)

        # Draw on surface
        surface.blit(rectangle, (self.pos.x - self.width/2, self.pos.y - self.height/2))

buttons: list[Button] = []
printButton = Button(pos=Vector2(WIDTH/2, HEIGHT/2), width=300, height=50, color=(100, 100, 100), backgroundTransparency=0, cornerRoundiness=.5, text="Hello")
buttons.append(printButton)

# Input info
mousePos = Vector2(0, 0)
mouseRel = Vector2(0, 0)
leftButtonPressed = False
rightButtonPressed = False

while True:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    mousePos = Vector2(mouseX, mouseY)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == MOUSEMOTION:
            mouseRel.x = event.rel[0]
            mouseRel.y = event.rel[1]
        
    leftButtonPressed, _, rightButtonPressed = pygame.mouse.get_pressed()

    window.fill(WHITE)

    if printButton.checkClick():
        print("Clicked!")
    if printButton.checkHold():
        print("Being hold!")
    if printButton.checkRelease():
        print("Button released!")

    for button in buttons:
        button.draw()

    drawText(f"FPS: {clock.get_fps():.0f}", Vector2(), fontSize=15)

    pygame.display.update()
    clock.tick(FPS)