import os
import pygame
import fborx
import argparse
import subprocess
import string
from PIL import Image
from PIL import ImageColor

parser = argparse.ArgumentParser(description='Photobooth.')
parser.add_argument('-f', '--full_screen', action='store_true', default=False)
parser.add_argument('-x', type=int, default=720)
parser.add_argument('-y', type=int, default=576)
parser.add_argument('-s', '--style', default='naranja_azul')
parser.add_argument('-b', '--border', default=0)
parser.add_argument('-tca', '--test_click_area', action='store_true', default=False)
parser.add_argument('-ti', '--test-image', action='store_true', default=False)
parser.add_argument('--prefix', default='test_session')
parser.add_argument('--raw_path', default='./raw')
parser.add_argument('--preview_path', default='./preview')


args = parser.parse_args()

size = (args.x, args.y)
_WHITE = (255, 255, 255)
_RED = (255, 0, 0)
_COUNT_DOWN_EVENT = pygame.USEREVENT + 1
_EXPECTED_RESOLUTION = (800, 480)
_RES_CX = (float(size[0])/_EXPECTED_RESOLUTION[0], float(size[1])/_EXPECTED_RESOLUTION[1])
print ("_RES_CX: %s,%s" % _RES_CX)
_TARGET_RESOLUTION = (800 * _RES_CX[0], 480 * _RES_CX[1])
print ("_TARGET_RESOLUTION: %s,%s" % _TARGET_RESOLUTION)
_RESULT_AREA = (198, 0, _TARGET_RESOLUTION[0]-30, _TARGET_RESOLUTION[1])
print ("_RESULT_AREA: %s,%s,%s,%s" % _RESULT_AREA)
_RESULT_AREA_SIZE = (_RESULT_AREA[2]-_RESULT_AREA[0], _RESULT_AREA[3]-_RESULT_AREA[1])
print ("_RESULT_AREA_SIZE: %s,%s" % _RESULT_AREA_SIZE)
_RESULT_AREA_MID_POINT = (_RESULT_AREA[0] + _RESULT_AREA_SIZE[0] / 2, _RESULT_AREA[1] + _RESULT_AREA_SIZE[1] / 2)
print ("_RESULT_AREA_MID_POINT: %s,%s" % _RESULT_AREA_MID_POINT)
_EXT = ".jpg"


def load_image(name, color_key=None, style=None):
    if not style:
        if os.path.isabs(name):
            fullname = name
        else:
            fullname = os.path.join(name)
    else:
        fullname = os.path.join('images', style, name)
    print ("image: \"%s\"" % fullname)
    image = pygame.image.load(fullname)
    image = image.convert()
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key, pygame.RLEACCEL)
    return image, image.get_rect()


class PhotoPaths:
    raw = None
    processed = None

    def __init__(self, raw, processed):
        self.raw = raw
        self.processed = processed


class PhotoNameGenerator:
    prefix = "test_session"
    photo_count = 0
    raw_path = "."
    preview_path = "."

    def __init__(self, prefix, raw_path, preview_path):
        self.prefix = prefix
        self.raw_path = raw_path
        self.preview_path = preview_path

    def next_photo_path(self):
        self.photo_count += 1
        photo_name = "%s-%s%s" % (self.prefix, self.photo_count, _EXT)
        raw = os.path.abspath(os.path.join(self.raw_path, self.prefix, photo_name))
        processed = os.path.abspath(os.path.join(self.preview_path, self.prefix, photo_name))
        return PhotoPaths(raw, processed)


class GameWindow:
    size = None
    screen = None
    clock = None
    windows = {}
    current_window = None
    last_result_image = None
    generator = None

    def __init__(self, default_size, full_screen=False):
        self.screen, self.size = fborx.get_screen(default_size, full_screen)
        self.clock = pygame.time.Clock()
        self.generator = PhotoNameGenerator(args.prefix, args.raw_path, args.preview_path)
        self.windows["welcome"] = Step('Slide1.JPG', [("menu", pygame.Rect((0, 0), self.size))])
        self.windows["menu"] = Step('Slide2.JPG', [("single-5",  pygame.Rect(0, 0, self.size[0]/2, self.size[1])),
                                                   ("multiple-1-5", pygame.Rect(self.size[0]/2, 0, self.size[0], self.size[1]))])
        self.windows["single"] = Step('Slide1.JPG', [("menu", pygame.Rect((0, 0), self.size))])
        self.windows["single-5"] = Step('Slide3.JPG', None, ('single-4', 2))
        self.windows["single-4"] = Step('Slide4.JPG', None, ('single-3', 1))
        self.windows["single-3"] = Step('Slide5.JPG', None, ('single-2', 1))
        self.windows["single-2"] = Step('Slide6.JPG', None, ('single-1', 1))
        self.windows["single-1"] = Step('Slide7.JPG', None, ('single-0', 1))
        self.windows["single-0"] = Step(None, command=('single-result', 'gphoto2 --capture-image-and-download --filename ${filename} --force-overwrite'))

        self.windows["multiple-1-5"] = Step('Slide8.JPG', None, ('multiple-1-4', 2))
        self.windows["multiple-1-4"] = Step('Slide9.JPG', None, ('multiple-1-3', 1))
        self.windows["multiple-1-3"] = Step('Slide10.JPG', None, ('multiple-1-2', 1))
        self.windows["multiple-1-2"] = Step('Slide11.JPG', None, ('multiple-1-1', 1))
        self.windows["multiple-1-1"] = Step('Slide12.JPG', None, ('multiple-1-0', 1))
        self.windows["multiple-1-0"] = Step(None, command=('multiple-2-5', 'gphoto2 --capture-image-and-download --filename ${filename} --force-overwrite'))

        self.windows["multiple-2-5"] = Step('Slide13.JPG', None, ('multiple-2-4', 2))
        self.windows["multiple-2-4"] = Step('Slide14.JPG', None, ('multiple-2-3', 1))
        self.windows["multiple-2-3"] = Step('Slide15.JPG', None, ('multiple-2-2', 1))
        self.windows["multiple-2-2"] = Step('Slide16.JPG', None, ('multiple-2-1', 1))
        self.windows["multiple-2-1"] = Step('Slide17.JPG', None, ('multiple-2-0', 1))
        self.windows["multiple-2-0"] = Step(None, command=('multiple-result', 'gphoto2 --capture-image-and-download --filename ${filename} --force-overwrite'))

        return_to_menu = pygame.Rect((0, self.size[1]-200), (200, self.size[1]))
        self.windows["multiple-result"] = Step('Slide18.JPG', [("menu", return_to_menu)], ('welcome', 20), result=True)
        self.windows["single-result"] = Step('Slide18.JPG', [("menu",  return_to_menu)], ('welcome', 20), result=True)

        self.current_window = self.windows["welcome"]

    def transition(self, e):
        next_window_name = self.current_window.transition(e, self)
        if next_window_name:
            self.current_window = self.windows[next_window_name]
        return self.current_window


class Step:

    start_time = 0
    image = None
    click_transitions = []
    time_transition = None
    event_transitions = []
    command = None
    command_running = False
    result = False
    transform_result_size = None
    transform_result_start = None

    def __init__(self, image_name, click_transitions=None, time_transition=None, event_transitions=None, command=None, result=False):
        self.start_time = 0
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

            if not self.transform_result_start and not self.transform_result_size:
                image_width = game_window.last_result_image[1].width
                image_height = game_window.last_result_image[1].height
                x_ratio = float(_RESULT_AREA_SIZE[0])/image_width
                y_ratio = float(_RESULT_AREA_SIZE[1])/image_height
                print ("x_ratio: %s" % x_ratio)
                print ("y_ratio: %s" % y_ratio)
                if x_ratio < y_ratio:
                    self.transform_result_size = (int(image_width * x_ratio * _RES_CX[0]), int(image_height * x_ratio * _RES_CX[1]))
                else:
                    self.transform_result_size = (int(image_width * y_ratio * _RES_CX[0]), int(image_height * y_ratio * _RES_CX[1]))

                print ("transform_result_size: %s,%s" % (self.transform_result_size[0], self.transform_result_size[1]))
                self.transform_result_start = (_RESULT_AREA_MID_POINT[0] - self.transform_result_size[0] / 2,
                                          _RESULT_AREA_MID_POINT[1] - self.transform_result_size[1] / 2)
            transformed_image = pygame.transform.scale(game_window.last_result_image[0], self.transform_result_size)
            pygame.draw.rect(game_window.screen, (0, 0, 0), (self.transform_result_start[0]-1, self.transform_result_start[1]-1, self.transform_result_size[0]+4, self.transform_result_size[1]+4))
            pygame.draw.rect(game_window.screen, _WHITE, (self.transform_result_start[0], self.transform_result_start[1], self.transform_result_size[0], self.transform_result_size[1]))
            game_window.screen.blit(transformed_image, self.transform_result_start)
        pygame.display.flip()

    def execute(self, game_window):
        if self.command and not self.command_running:
            if args.test_image:
                photo_name = PhotoPaths('images/maxresdefault.jpg', 'images/maxresdefault-processed.jpg')
            else:
                self.command_running = True
                photo_name = game_window.generator.next_photo_path()
                command = string.Template(self.command[1]).safe_substitute(filename=photo_name.raw)
                print ("executing: \"%s\"" % command)
                subprocess.call(command.split(' '))
                self.command_running = False
            processed_path = self.process_image(photo_name)
            game_window.last_result_image = load_image(processed_path, -1)
            self.start_time = 0
            return self.command[0]

    def transition(self, e, game_window):
        if self.command:
            self.start_time = 0
            return self.execute(game_window)
        if self.click_transitions and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for tran in self.click_transitions:
                if tran[1].collidepoint(e.pos):
                    self.start_time = 0
                    return tran[0]
        if self.time_transition:
            if e.type == _COUNT_DOWN_EVENT:
                self.start_time += 1
                if self.start_time == self.time_transition[1]:
                    self.start_time = 0
                    return self.time_transition[0]
        return None

    def process_image (self, image):
        banner_path = 'images/banner.jpg'
        banner = Image.open(banner_path)
        print("banner", banner.format, banner.size, banner.mode)
        im = Image.open(image.raw)
        print("image", im.format, im.size, im.mode)

        new_height = int((4 * (im.size[1] + 250)) - (2 * im.size[0]))
        new_width = int(new_height * 1.5)
        border = int((new_width-im.size[0])/2)
        print("new", new_width, new_height, border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        new_im.paste(im, (border, border))
        new_im.paste(banner, (int(new_width/2 - banner.size[0]/2), im.size[1]+border))
        processed_path = image.processed
        parent_dir = os.path.dirname(processed_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        new_im.save(processed_path)
        return processed_path



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
