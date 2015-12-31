import os
import pygame
import fborx
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Photobooth.')
parser.add_argument('-f', '--full_screen', action='store_true', default=False)
parser.add_argument('-x', type=int, default=720)
parser.add_argument('-y', type=int, default=576)
parser.add_argument('-s', '--style', default='naranja_azul')
parser.add_argument('-b', '--border', default=0)
parser.add_argument('-t', action='store_true', default=False)
args = parser.parse_args()

size = (args.x, args.y)
_WHITE = (255, 255, 255)
_RED = (255, 0, 0)
_COUNTDOWNEVENT = pygame.USEREVENT + 1

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
        self.windows["welcome"] = Step('Slide1.PNG', [("menu", pygame.Rect((0, 0), size))])
        self.windows["menu"] = Step('Slide2.PNG', [("single-result",  pygame.Rect(0, 0, self.size[0]/2, self.size[1])),
                                                   ("multiple-1-5", pygame.Rect(self.size[0]/2, 0, self.size[0], self.size[1]))])
        self.windows["single"] = Step('Slide1.PNG', [("menu", pygame.Rect((0, 0), size))])
        self.windows["multiple-1-5"] = Step('Slide3.PNG', None, ('multiple-1-4', 1))
        self.windows["multiple-1-4"] = Step('Slide4.PNG', None, ('multiple-1-3', 1))
        self.windows["multiple-1-3"] = Step('Slide5.PNG', None, ('multiple-1-2', 1))
        self.windows["multiple-1-2"] = Step('Slide6.PNG', None, ('multiple-1-1', 1))
        self.windows["multiple-1-1"] = Step('Slide7.PNG', None, ('multiple-1-0', 1))
        self.windows["multiple-1-0"] = Step(None, command=('multiple-2-5', 'gphoto2 --capture-image-and-download --filename="A.jpg" --force-overwrite'))
        self.windows["multiple-2-5"] = Step('Slide8.PNG', None, ('multiple-2-4', 1))
        self.windows["multiple-2-4"] = Step('Slide9.PNG', None, ('multiple-2-3', 1))
        self.windows["multiple-2-3"] = Step('Slide10.PNG', None, ('multiple-2-2', 1))
        self.windows["multiple-2-2"] = Step('Slide11.PNG', None, ('multiple-2-1', 1))
        self.windows["multiple-2-1"] = Step('Slide12.PNG', None, ('multiple-3-5', 1))
        self.windows["multiple-3-5"] = Step('Slide13.PNG', None, ('multiple-3-4', 1))
        self.windows["multiple-3-4"] = Step('Slide14.PNG', None, ('multiple-3-3', 1))
        self.windows["multiple-3-3"] = Step('Slide15.PNG', None, ('multiple-3-2', 1))
        self.windows["multiple-3-2"] = Step('Slide16.PNG', None, ('multiple-3-1', 1))
        self.windows["multiple-3-1"] = Step('Slide17.PNG', None, ('multiple-4-5', 1))
        self.windows["multiple-4-5"] = Step('Slide18.PNG', None, ('multiple-4-4', 1))
        self.windows["multiple-4-4"] = Step('Slide19.PNG', None, ('multiple-4-3', 1))
        self.windows["multiple-4-3"] = Step('Slide20.PNG', None, ('multiple-4-2', 1))
        self.windows["multiple-4-2"] = Step('Slide21.PNG', None, ('multiple-4-1', 1))
        self.windows["multiple-4-1"] = Step('Slide22.PNG', None, ('multiple-result', 1))
        self.windows["multiple-result"] = Step('Slide23.PNG', [("menu",  pygame.Rect((0, self.size[1]-200), (200, self.size[1])))], ('welcome', 20))
        self.windows["single-result"] = Step('Slide24.PNG', [("menu",  pygame.Rect((0, self.size[1]-200), (200, self.size[1])))], ('welcome', 20))

        self.current_window = self.windows["welcome"]

    def transition(self, e):
        next_window_name = self.current_window.transition(e)
        if next_window_name:
            self.current_window = self.windows[next_window_name]
            self.current_window.execute()
        return self.current_window


class Step:

    start_time = None
    image = None
    click_transitions = []
    time_transitions = None
    event_transitions = []
    command = None
    command_running = False

    def __init__(self, image_name, click_transitions=None, time_transitions=None, event_transitions=None, command=None):
        self.start_time = None
        if image_name:
            self.image, singleRect = load_image(image_name, -1)
        self.click_transitions = click_transitions
        self.time_transitions = time_transitions
        self.event_transitions = event_transitions
        self.command = command

    def paint(self, game_window):
        game_window.screen.fill(_WHITE)
        if self.image:
            game_window.screen.blit(pygame.transform.scale(self.image, size), (0, 0))
        if args.t and self.click_transitions:
            s = pygame.Surface(game_window.size)
            s.set_alpha(128)
            s.fill(_WHITE)
            for tran in self.click_transitions:
                pygame.draw.rect(s, _RED, tran[1], 10)
            game_window.screen.blit(s, (0, 0))

        pygame.display.flip()

    def execute(self):
        if self.command and not self.command_running:
            self.command_running = True
            subprocess.call(self.command[1].split(' '), shell=True)
            self.command_running = False
            return self.command[0]

    def transition(self, e):
        if self.click_transitions and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for tran in self.click_transitions:
                if tran[1].collidepoint(e.pos):
                    return tran[0]
        if self.time_transitions:
            if not self.start_time:
                self.start_time = 0
            if e.type == _COUNTDOWNEVENT:
                self.start_time += 1
                if self.start_time == self.time_transitions[1]:
                    return self.time_transitions[0]
        return None

    def tick(self):
        pass

args = parser.parse_args()
gw = GameWindow(size, args.full_screen)
pygame.time.set_timer(_COUNTDOWNEVENT, 1000)
running = True
while running:

    gw.current_window.paint(gw)
    gw.current_window.tick()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        gw.transition(event)
        gw.clock.tick(60)

# make sure to call pygame.quit() if using the framebuffer to get back to your terminal
pygame.quit()
