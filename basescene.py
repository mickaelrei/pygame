import pygame
from pygame.locals import *
import sys

class BaseScene:
    def __init__(self, width: int=600, height: int=600, title: str="", FPS: int=60) -> None:
        '''
        Start a scene with the given width, height, title and FPS
        '''
        pygame.init()
        self.width = width
        self.height = height
        self.window: pygame.Surface = pygame.display.set_mode((width, height))
        self.__FPS = FPS
        self.clock = pygame.time.Clock()
        if type(title) == str and len(title) > 0:
            pygame.display.set_caption(title)

    def setup(self) -> None:
        '''
        Setup variables and constants
        '''
        pass

    def render(self) -> None:
        '''
        Method to render graphics such as shapes and texts
        '''
        pass

    def update(self) -> None:
        '''
        Method to update variables
        '''
        # Update frame
        pygame.display.update()
        self.clock.tick(self.__FPS)

    def get_input(self) -> None:
        '''
        Method to get input
        '''
        # Get input for exiting the window
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.close()

    def close(self) -> None:
        '''
        Method to stop pygame
        '''
        # Stop pygame
        pygame.quit()
        sys.exit("Closing game")

if __name__ == "__main__":
    game = BaseScene(title="Base Scene")

    while True:
        game.get_input()
        game.render()
        game.update()