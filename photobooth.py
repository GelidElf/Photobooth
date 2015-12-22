import os
import time
import pygame

import fborx
import argparse

# this will open a 800x800 window if xserver is running or fullscreen fb if not

backgroundx = 1000;
backgroundy = 500;

parser = argparse.ArgumentParser(description='Photobooth.')
parser.add_argument('-f', '--fullscreen', action='store_true', default=False)
parser.add_argument('-x', type=int, default=backgroundx)
parser.add_argument('-y', type=int, default=backgroundy)
args = parser.parse_args()

size = (args.x, args.y)
# size = None


def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, image.get_rect()

class GameWindow:
    size = None
    screen = None
    clock = None

    def __init__(self, s,fullscreen=False):
        self.screen,self.size = fborx.getScreen(s,fullscreen);
        self.clock = pygame.time.Clock()


class MainMenuScreen:
    game_window = None
    border = None
    imageSize = None
    singleImage = None
    singleButton = None
    multiButton = None

    def __init__(self, game_window):
        self.game_window = game_window
        self.border = 30
        self.imageSize = (int(game_window.size[0] / 2 - self.border - self.border / 2), int(game_window.size[1] - 2 * self.border))
        self.singleImage, self.singleRect = load_image('single-photo.png', -1)
        self.singleImage = pygame.transform.scale(self.singleImage,self.imageSize)
        self.multiImage, self.multiRect = load_image('multi-photo.png', -1)
        self.multiImage = pygame.transform.scale(self.multiImage,self.imageSize)

    def tick(self):
        #self.game_window.clock.tick(2)
        pass

    def paint(self):
        singlePhotoBounds = (self.border, self.border, self.imageSize[0], self.imageSize[1])
        self.singleButton = self.game_window.screen.blit(self.singleImage,(singlePhotoBounds[0],singlePhotoBounds[1]))
        multiPhotoBoundsStart = (self.game_window.size[0] - self.border - self.imageSize[0], self.border)
        multiPhotoBounds = (multiPhotoBoundsStart[0], multiPhotoBoundsStart[1], self.imageSize[0], self.imageSize[1])
        self.multiButton = self.game_window.screen.blit(self.multiImage,(multiPhotoBounds[0],multiPhotoBounds[1]))
        pygame.display.flip()


class SingleClockScreen:
    counter, text = 5, '5'.center(3)
    gw = None
    font = None
    image_5 = None
    image_4 = None
    image_3 = None
    image_2 = None
    image_1 = None

    def __init__(self,game_window,start=None):
        self.gw = game_window
        if start:
            self.counter, self.text = start, str(start).center(3)
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.font = pygame.font.SysFont('Consolas', 400)

    def tick(self):
        self.counter -= 1
        self.text = str(self.counter).center(3) if self.counter > 0 else 'smile!'
        #self.gw.clock.tick(60)
        time.sleep(1)

    def paint(self):
        self.gw.screen.fill((255, 255, 255))
        display_text = self.font.render(self.text, True, (0, 0, 0))
        display_size = display_text.get_size()
        position = ((self.gw.size[0]-display_size[0])/2, (self.gw.size[1]-display_size[1])/2)
        self.gw.screen.blit(display_text, position)
        pygame.display.flip()



args = parser.parse_args()
gw = GameWindow(size,args.fullscreen)
mms = MainMenuScreen(gw)
scs = SingleClockScreen(gw)
mms.paint()
# this code just waits for the ESC key (isn't beauty with the loop, but works for now)
running = True
window = mms
while running:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        if pygame.mouse.get_pressed()[0] == 1:
            if mms.singleButton.collidepoint(pygame.mouse.get_pos()):
                print('single button pressed')
                window = scs
            if mms.multiButton.collidepoint(pygame.mouse.get_pos()):
                print('multiple button pressed')
    window.tick()
    window.paint()

# make sure to call pygame.quit() if using the framebuffer to get back to your terminal
pygame.quit()
