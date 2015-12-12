import os, sys
import pygame
from pygame.locals import *

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')


class SinglePhoto(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = self.load_image('single-photo.png', -1)
        self.pellets = 0

    def load_image(self, name, colorkey=None):
        fullname = os.path.join('images', name)
        image = pygame.image.load(fullname)
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image, image.get_rect()

class MultiPhoto(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = self.load_image('multi-photo.png', -1)
        self.pellets = 0

    def load_image(self, name, colorkey=None):
        fullname = os.path.join('images', name)
        image = pygame.image.load(fullname)
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image, image.get_rect()


class PyManMain:
    """The Main PyMan Class - This class handles the main
    initialization and creating of the Game."""

    def __init__(self, width=640,height=480):
        """Initialize"""
        """Initialize PyGame"""
        pygame.init()
        """Set the window Size"""
        self.width = width
        self.height = height
        self.single_photo = None
        self.single_photo_sprites = None
        """Create the Screen"""
        self.screen = pygame.display.set_mode((self.width, self.height))

    def mainloop(self):
        """Load All of our Sprites"""
        self.load_sprites();
        """This is the Main Loop of the Game"""
        while 1:
            self.single_photo_sprites.draw(self.screen)
            pygame.display.flip()
            # proceed events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                # handle MOUSEBUTTONUP
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    # get a list of all sprites that are under the mouse cursor
                    clicked_sprites = [s for s in sprites if s.single_photo.collidepoint(pos)]
                    # do something with the clicked sprites...


    def load_sprites(self):
        """Load the sprites that we need"""
        self.single_photo = SinglePhoto()
        self.single_photo_sprites = pygame.sprite.RenderPlain(self.single_photo)

        self.multi_photo = MultiPhoto()
        self.multi_photo_sprites = pygame.sprite.RenderPlain(self.multi_photo)

if __name__ == "__main__":
    MainWindow = PyManMain()
    MainWindow.mainloop()
