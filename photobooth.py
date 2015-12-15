import pygame
from pygame.locals import *
import fborx
import os

# this will open a 800x800 window if xserver is running or fullscreen fb if not

backgroundx = 1000;
backgroundy = 500;
size = (backgroundx, backgroundy);


class GameWindow:
    size = None
    screen = None

    def __init__(self, size):
        self.size = size
        self.screen = fborx.getScreen(size);


class MainMenuScreen:
    gameWindow = None
    border = None
    imageSize = None

    def __init__(self, gameWindow):
        self.gameWindow = gameWindow
        self.border = 30
        self.imageSize = (int(gameWindow.size[0] / 2 - self.border - self.border / 2), int(gameWindow.size[1] - 2 * self.border))
        self.singleImage, self.singleRect = self.load_image('single-photo.png', -1)
        self.multiImage, self.multiRect = self.load_image('multi-photo.png', -1)

    def load_image(self, name, colorkey=None):
        fullname = os.path.join('images', name)
        image = pygame.image.load(fullname)
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image, image.get_rect()

    def paint(self):
        singlePhotoBounds = (self.border, self.border, self.imageSize[0], self.imageSize[1])
        #pygame.draw.rect(self.gameWindow.screen, (255, 0, 0), singlePhotoBounds)
        self.gameWindow.screen.blit(pygame.transform.scale(self.singleImage,self.imageSize),(singlePhotoBounds[0],singlePhotoBounds[1]))
        multiPhotoBoundsStart = (self.gameWindow.size[0] - self.border - self.imageSize[0], self.border)
        multiPhotoBounds = (multiPhotoBoundsStart[0], multiPhotoBoundsStart[1], self.imageSize[0], self.imageSize[1])
        #pygame.draw.rect(self.gameWindow.screen, (255, 0, 0), multiPhotoBounds)
        self.gameWindow.screen.blit(pygame.transform.scale(self.multiImage,self.imageSize),(multiPhotoBounds[0],multiPhotoBounds[1]))
        pygame.display.flip()

gw = GameWindow(size)
mms = MainMenuScreen(gw)
mms.paint()
# this code just waits for the ESC key (isn't beauty with the loop, but works for now)
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        if pygame.mouse.get_pressed()[0] == 1:
            if play_big.collidepoint(pygame.mouse.get_pos()):
                print('button pressed')

# make sure to call pygame.quit() if using the framebuffer to get back to your terminal
pygame.quit()
