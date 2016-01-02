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
parser.add_argument('-tca', '--test_click_area', action='store_true', default=False)
parser.add_argument('-ti', '--test-image', action='store_true', default=False)
args = parser.parse_args()

size = (args.x, args.y)
_WHITE = (255, 255, 255)
_RED = (255, 0, 0)
_COUNT_DOWN_EVENT = pygame.USEREVENT + 1
_RESULT_AREA = (198, 0, size[0]-30, size[1])
_RESULT_AREA_SIZE = (_RESULT_AREA[2]-_RESULT_AREA[0], _RESULT_AREA[3]-_RESULT_AREA[1])
_RESULT_AREA_MID_POINT = (_RESULT_AREA[0] + _RESULT_AREA_SIZE[0] / 2, _RESULT_AREA[1] + _RESULT_AREA_SIZE[1] / 2)


def load_image(name, color_key=None, style=None):
    if not style:
        fullname = os.path.join('images', name)
    else:
        fullname = os.path.join('images', style, name)
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
    last_result_image = None

    def __init__(self, s, full_screen=False):
        self.screen, self.size = fborx.get_screen(s, full_screen)
        self.clock = pygame.time.Clock()
        self.windows["welcome"] = Step('Slide1.PNG', [("menu", pygame.Rect((0, 0), size))])
        self.windows["menu"] = Step('Slide2.PNG', [("single-5",  pygame.Rect(0, 0, self.size[0]/2, self.size[1])),
                                                   ("multiple-1-5", pygame.Rect(self.size[0]/2, 0, self.size[0], self.size[1]))])
        self.windows["single"] = Step('Slide1.PNG', [("menu", pygame.Rect((0, 0), size))])
        self.windows["single-5"] = Step('Slide3 (2).PNG', None, ('single-4', 2))
        self.windows["single-4"] = Step('Slide4 (2).PNG', None, ('single-3', 1))
        self.windows["single-3"] = Step('Slide5 (2).PNG', None, ('single-2', 1))
        self.windows["single-2"] = Step('Slide6 (2).PNG', None, ('single-1', 1))
        self.windows["single-1"] = Step('Slide7 (2).PNG', None, ('single-0', 1))
        self.windows["single-0"] = Step(None, command=('single-result', 'gphoto2 --capture-image-and-download --filename="A.jpg" --force-overwrite'))

        self.windows["multiple-1-5"] = Step('Slide3.PNG', None, ('multiple-1-4', 2))
        self.windows["multiple-1-4"] = Step('Slide4.PNG', None, ('multiple-1-3', 1))
        self.windows["multiple-1-3"] = Step('Slide5.PNG', None, ('multiple-1-2', 1))
        self.windows["multiple-1-2"] = Step('Slide6.PNG', None, ('multiple-1-1', 1))
        self.windows["multiple-1-1"] = Step('Slide7.PNG', None, ('multiple-1-0', 1))
        self.windows["multiple-1-0"] = Step(None, command=('multiple-2-5', 'gphoto2 --capture-image-and-download --filename="A.jpg" --force-overwrite'))

        self.windows["multiple-2-5"] = Step('Slide8.PNG', None, ('multiple-2-4', 2))
        self.windows["multiple-2-4"] = Step('Slide9.PNG', None, ('multiple-2-3', 1))
        self.windows["multiple-2-3"] = Step('Slide10.PNG', None, ('multiple-2-2', 1))
        self.windows["multiple-2-2"] = Step('Slide11.PNG', None, ('multiple-2-1', 1))
        self.windows["multiple-2-1"] = Step('Slide12.PNG', None, ('multiple-3-5', 1))

        self.windows["multiple-3-5"] = Step('Slide13.PNG', None, ('multiple-3-4', 2))
        self.windows["multiple-3-4"] = Step('Slide14.PNG', None, ('multiple-3-3', 1))
        self.windows["multiple-3-3"] = Step('Slide15.PNG', None, ('multiple-3-2', 1))
        self.windows["multiple-3-2"] = Step('Slide16.PNG', None, ('multiple-3-1', 1))
        self.windows["multiple-3-1"] = Step('Slide17.PNG', None, ('multiple-4-5', 1))

        self.windows["multiple-4-5"] = Step('Slide18.PNG', None, ('multiple-4-4', 2))
        self.windows["multiple-4-4"] = Step('Slide19.PNG', None, ('multiple-4-3', 1))
        self.windows["multiple-4-3"] = Step('Slide20.PNG', None, ('multiple-4-2', 1))
        self.windows["multiple-4-2"] = Step('Slide21.PNG', None, ('multiple-4-1', 1))
        self.windows["multiple-4-1"] = Step('Slide22.PNG', None, ('multiple-result', 1))

        self.windows["multiple-result"] = Step('Slide23.PNG', [("menu",  pygame.Rect((0, self.size[1]-200), (200, self.size[1])))], ('welcome', 20), result=True)
        self.windows["single-result"] = Step('Slide24.PNG', [("menu",  pygame.Rect((0, self.size[1]-200), (200, self.size[1])))], ('welcome', 20), result=True)

        self.current_window = self.windows["welcome"]

    def transition(self, e):
        next_window_name = self.current_window.transition(e)
        if next_window_name:
            self.current_window = self.windows[next_window_name]
            self.current_window.execute(self)
        return self.current_window


class Step:

    start_time = None
    image = None
    click_transitions = []
    time_transition = None
    event_transitions = []
    command = None
    command_running = False
    result = False

    def __init__(self, image_name, click_transitions=None, time_transition=None, event_transitions=None, command=None, result=False):
        self.start_time = None
        if image_name:
            self.image, singleRect = load_image(image_name, -1, args.style)
        self.click_transitions = click_transitions
        self.time_transition = time_transition
        self.event_transitions = event_transitions
        self.command = command
        self.result = result

    def paint(self, game_window):
        game_window.screen.fill(_WHITE)
        if self.image:
            game_window.screen.blit(pygame.transform.scale(self.image, size), (0, 0))
        if args.test_click_area and self.click_transitions:
            s = pygame.Surface(game_window.size)
            s.set_alpha(128)
            s.fill(_WHITE)
            for tran in self.click_transitions:
                pygame.draw.rect(s, _RED, tran[1], 10)
            game_window.screen.blit(s, (0, 0))
        if self.result and game_window.last_result_image:
            x_ratio = _RESULT_AREA_SIZE[0]/game_window.last_result_image[1][2]
            y_ratio = _RESULT_AREA_SIZE[1]/game_window.last_result_image[1][3]
            if x_ratio < y_ratio:
                transform_result_size = (int(game_window.last_result_image[1][2] * x_ratio),
                                         int(game_window.last_result_image[1][3] * x_ratio))
            else:
                transform_result_size = (int(game_window.last_result_image[1][2] * y_ratio),
                                         int(game_window.last_result_image[1][3] * y_ratio))
            transform_result_start = (_RESULT_AREA_MID_POINT[0] - transform_result_size[0] / 2,
                                      _RESULT_AREA_MID_POINT[1] - transform_result_size[1] / 2)
            transformed_image = pygame.transform.scale(game_window.last_result_image[0], transform_result_size)
            game_window.screen.blit(transformed_image, transform_result_start)
        pygame.display.flip()

    def execute(self, game_window):

        if self.command and not self.command_running:
            if args.test_image:
                game_window.last_result_image = load_image('maxresdefault.jpg', -1)
                self.time_transition = (self.command[0], 1)
            else:
                self.command_running = True
                subprocess.call(self.command[1].split(' '), shell=True)
                self.command_running = False
                return self.command[0]

    def transition(self, e):
        if self.click_transitions and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for tran in self.click_transitions:
                if tran[1].collidepoint(e.pos):
                    return tran[0]
        if self.time_transition:
            if not self.start_time:
                self.start_time = 0
            if e.type == _COUNT_DOWN_EVENT:
                self.start_time += 1
                if self.start_time == self.time_transition[1]:
                    self.start_time = 0
                    return self.time_transition[0]
        return None


args = parser.parse_args()
gw = GameWindow(size, args.full_screen)
pygame.time.set_timer(_COUNT_DOWN_EVENT, 1000)
running = True
while running:

    gw.current_window.paint(gw)
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
