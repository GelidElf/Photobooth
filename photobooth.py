import os
import time
import pygame
import fborx
import argparse

parser = argparse.ArgumentParser(description='Photobooth.')
parser.add_argument('-f', '--full_screen', action='store_true', default=False)
parser.add_argument('-x', type=int, default=800)
parser.add_argument('-y', type=int, default=480)
parser.add_argument('-s', '--style', default='naranja_azul')
parser.add_argument('-b', '--border', default=0)
args = parser.parse_args()

size = (args.x, args.y)


def load_image(name, color_key=None):
    fullname = os.path.join('images', args.style, name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key, pygame.RLEACCEL)
    return image, image.get_rect()


class GameWindow:
    size = None
    screen = None
    clock = None
    windows = {}
    current_window = None

    def __init__(self, s, full_screen=False):
        self.screen, self.size = fborx.get_screen(s, full_screen)
        self.clock = pygame.time.Clock()
        self.windows["menu"] = MainMenuScreen(self)
        self.windows["single"] = SingleClockScreen(self)
        self.windows["multiple"] = MultipleClockScreen(self)
        self.current_window = self.windows["menu"]

    def transition(self, event):
        self.current_window = self.windows[self.current_window.transition(event)]
        return self.current_window


class MainMenuScreen:
    game_window = None
    border = None
    welcome_image = None
    menu_image = None
    single_button = None
    multi_button = None

    def __init__(self, game_window):
        self.game_window = game_window
        self.border = args.border
        self.image_size = game_window.size
        # (int(game_window.size[0] / 2 - self.border - self.border / 2), int(game_window.size[1] - 2 * self.border))
        self.welcome_image, singleRect = load_image('Slide1.png', -1)
        self.welcome_image = pygame.transform.scale(self.welcome_image, self.image_size)
        self.menu_image, self.multiRect = load_image('Slide2.png', -1)
        self.menu_image = pygame.transform.scale(self.menu_image, self.image_size)

    def tick(self):
        # self.game_window.clock.tick(2)
        pass

    def paint(self):
        self.game_window.screen.blit(self.welcome_image, (0, 0))
        self.single_button = (self.border, self.border, self.image_size[0]/2, self.image_size[1])
        multi_photo_bounds_start = (self.game_window.size[0] - self.border - self.image_size[0], self.border)
        self.multi_button = (multi_photo_bounds_start[0], multi_photo_bounds_start[1], self.image_size[0], self.image_size[1])
        pygame.display.flip()

    def transition(self, event):
        if pygame.mouse.get_pressed()[0] == 1:
            if self.singleButton.collidepoint(pygame.mouse.get_pos()):
                print('single button pressed')
                return "single"
            if self.multiButton.collidepoint(pygame.mouse.get_pos()):
                print('multiple button pressed')
                return "multiple"
        return "menu"


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
gw = GameWindow(size, args.full_screen)
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
