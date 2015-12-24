import os
import time
import pygame
import fborx
import argparse

parser = argparse.ArgumentParser(description='Photobooth.')
parser.add_argument('-f', '--fullscreen', action='store_true', default=False)
parser.add_argument('-x', type=int, default=1000)
parser.add_argument('-y', type=int, default=500)
args = parser.parse_args()

size = (args.x, args.y)


def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, image.get_rect()


class GameWindow:
    size = None
    screen = None
    clock = None
    windows = None
    current_window = None;

    def __init__(self, s, full_screen=False):
        self.screen, self.size = fborx.getScreen(s, full_screen);
        self.clock = pygame.time.Clock()
        self.windows = {}
        self.windows["menu"] = MainMenuScreen(self)
        self.windows["single"] = SingleClockScreen(self)
        self.windows["multiple"] = MultipleClockScreen(self)
        self.current_window = self.windows["menu"]

    def transition(self, event):
        self.current_window.transition(event)
        return self.current_window


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
        self.singleImage = pygame.transform.scale(self.singleImage, self.imageSize)
        self.multiImage, self.multiRect = load_image('multi-photo.png', -1)
        self.multiImage = pygame.transform.scale(self.multiImage, self.imageSize)

    def tick(self):
        # self.game_window.clock.tick(2)
        pass

    def paint(self):
        single_photo_bounds = (self.border, self.border, self.imageSize[0], self.imageSize[1])
        self.singleButton = self.game_window.screen.blit(self.singleImage, (single_photo_bounds[0], single_photo_bounds[1]))
        multi_photo_boundsStart = (self.game_window.size[0] - self.border - self.imageSize[0], self.border)
        multi_photo_bounds = (multi_photo_boundsStart[0], multi_photo_boundsStart[1], self.imageSize[0], self.imageSize[1])
        self.multiButton = self.game_window.screen.blit(self.multiImage, (multi_photo_bounds[0], multi_photo_bounds[1]))
        pygame.display.flip()

    def transition(self, event):
        if pygame.mouse.get_pressed()[0] == 1:
            if self.singleButton.collidepoint(pygame.mouse.get_pos()):
                print('single button pressed')
                return SingleClockScreen(self.game_window)
            if self.multiButton.collidepoint(pygame.mouse.get_pos()):
                print('multiple button pressed')
        return self


class SingleClockScreen:
    counter, text = 5, '5'.center(3)
    gw = None
    font = None
    image_5 = None
    image_4 = None
    image_3 = None
    image_2 = None
    image_1 = None

    def __init__(self, game_window, start=None):
        self.gw = game_window
        if start:
            self.counter, self.text = start, str(start).center(3)
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.font = pygame.font.SysFont('Consolas', 400)

    def tick(self):
        self.counter -= 1
        self.text = str(self.counter).center(3) if self.counter > 0 else 'smile!'
        # self.gw.clock.tick(60)
        time.sleep(1)

    def paint(self):
        self.gw.screen.fill((255, 255, 255))
        display_text = self.font.render(self.text, True, (0, 0, 0))
        display_size = display_text.get_size()
        position = ((self.gw.size[0] - display_size[0]) / 2, (self.gw.size[1] - display_size[1]) / 2)
        self.gw.screen.blit(display_text, position)
        pygame.display.flip()


class MultipleClockScreen:
    gw = None

    def __init__(self, game_window):
        self.gw = game_window


args = parser.parse_args()
gw = GameWindow(size, args.fullscreen)
running = True
window = gw.current_window
while running:

    window.paint()
    window.tick()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        gw.transition(event)

# make sure to call pygame.quit() if using the framebuffer to get back to your terminal
pygame.quit()
