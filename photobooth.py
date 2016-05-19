import os
import pygame
import fborx
from processor_pillow import Processor
import argparse
import subprocess
import string

gphoto_command = 'gphoto2 --capture-image-and-download --filename ${filename} --force-overwrite'
print_command = ' lpr -P Canon_CP910_ipp ${filename}'

_ROOT_DIR = os.path.dirname(__file__)
print "ROOT DIR %s" % _ROOT_DIR
_WHITE = (255, 255, 255)
_RED = (255, 0, 0)
_COUNT_DOWN_EVENT = pygame.USEREVENT + 1
_EXPECTED_RESOLUTION = (800, 480)
_EXT = ".jpg"

parser = argparse.ArgumentParser(description='Photobooth.')
parser.add_argument('-f', '--full_screen', action='store_true', default=False)
parser.add_argument('-x', type=int, default=720)
parser.add_argument('-y', type=int, default=576)
parser.add_argument('-s', '--style', default='blanco_negro')
parser.add_argument('-b', '--border', default=0)
parser.add_argument('-tca', '--test_click_area', action='store_true', default=False)
parser.add_argument('-ti', '--test-image', action='store_true', default=False)
parser.add_argument('--prefix', default='test_session')
parser.add_argument('--output_path', default=_ROOT_DIR)

args = parser.parse_args()

SIZE = (args.x, args.y)
RES_AREA = None


def update_globals(size):
    global SIZE
    global RES_AREA
    SIZE = size
    res_cx = (float(SIZE[0]) / _EXPECTED_RESOLUTION[0], float(SIZE[1]) / _EXPECTED_RESOLUTION[1])
    print("res_cx: %s,%s" % res_cx)
    border = (30 * res_cx[0])
    RES_AREA = (198 * res_cx[0], border, SIZE[0] - border, SIZE[1] - border)
    print("RES_AREA: %s,%s,%s,%s" % RES_AREA)


def load_image(name, style=None):
    if not style:
        if os.path.isabs(name):
            fullname = name
        else:
            fullname = os.path.join(name)
    else:
        fullname = os.path.join(_ROOT_DIR, 'images', style, name)
    print("image: \"%s\"" % fullname)
    image = pygame.image.load(fullname).convert()
    return image, image.get_rect()


class PhotoBundle:
    raw = None
    processed = None

    def __init__(self, raw, processed):
        self.raw = raw
        self.processed = processed

    def __str__(self):
        return "[%s:%s" % (self.processed, self.raw)


class PhotoNameGenerator:
    prefix = None
    photo_count = 0
    raw_path = None
    preview_path = None
    last_photo_bundle = None
    banner_path = None
    raw_queue = None

    def __init__(self, prefix, output_path):
        self.prefix = prefix
        session_path = os.path.join(output_path, self.prefix)
        if not os.path.exists(session_path):
            os.makedirs(session_path)
            print "ERROR: Session path '%s' created, Move the banner to the path" % session_path
            exit (0)
        self.banner_path = os.path.join(session_path, 'banner.jpg')
        self.raw_path = os.path.join(session_path, "raw")
        if not os.path.exists(self.raw_path):
            os.makedirs(self.raw_path)
        self.preview_path = os.path.join(session_path, "preview")
        if not os.path.exists(self.preview_path):
            os.makedirs(self.preview_path)
        self.raw_queue = []

    def create(self, number_photos=1):
        self.raw_queue = []
        if args.test_image:
            for _ in range(number_photos):
                self.raw_queue.append(os.path.abspath(os.path.join(_ROOT_DIR, 'images/maxresdefault.jpg')))
            processed = os.path.abspath(os.path.join(_ROOT_DIR, 'images/maxresdefault-processed%s.jpg' % number_photos))
        else:
            for _ in range(number_photos):
                self.photo_count += 1
                photo_name = "%s-%s%s" % (self.prefix, self.photo_count, _EXT)
                self.raw_queue.append(os.path.abspath(os.path.join(self.raw_path, photo_name)))
            processed = os.path.abspath(os.path.join(self.preview_path, photo_name))
        self.last_photo_bundle = PhotoBundle(list(self.raw_queue), processed)
        print("created %s" % self.last_photo_bundle)


class GameWindow:
    screen = None
    clock = None
    windows = {}
    current_step = None
    screen_surface = None
    generator = None
    last_result_image = None
    processor = None

    def __init__(self, screen):
        self.generator = PhotoNameGenerator(args.prefix, args.output_path)
        self.processor = Processor(self.generator.banner_path)
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.windows["welcome"] = Step('Slide1.JPG', [("menu", pygame.Rect((0, 0), self.screen.get_size()))])
        self.windows["menu"] = Step('Slide2.JPG', [
            ("single-5", pygame.Rect(self.screen.get_size()[0] * 0.25, 0, self.screen.get_size()[0] * 0.5, self.screen.get_size()[1]), 1)])
        self.windows["single"] = Step('Slide1.JPG', [("menu", pygame.Rect((0, 0), self.screen.get_size()))])
        self.windows["single-5"] = Step('Slide3.JPG', None, ('single-4', 2))
        self.windows["single-4"] = Step('Slide4.JPG', None, ('single-3', 1))
        self.windows["single-3"] = Step('Slide5.JPG', None, ('single-2', 1))
        self.windows["single-2"] = Step('Slide6.JPG', None, ('single-1', 1))
        self.windows["single-1"] = Step('Slide7.JPG', None, ('smile', 1))
        self.windows["smile"] = Step('Slide8.JPG', None, command=('process', gphoto_command))
        self.windows["process"] = Step('Slide9.JPG', None, ('single-result', 1))

        return_to_menu = pygame.Rect((0, self.screen.get_size()[1] - 200), (200, self.screen.get_size()[1]))
        self.windows["single-result"] = Step('Slide10.JPG', [("menu", return_to_menu)], ('welcome', 20), result=True)

        self.current_step = self.windows["welcome"]
        self.screen_surface = pygame.Surface(self.screen.get_size())
        self.paint(self.current_step.screen(self.screen_surface, self.generator.last_photo_bundle))

    def transition(self, e):
        next_window_name = self.current_step.transition(e, self)
        if next_window_name:
            self.current_step = self.windows[next_window_name]
            self.paint(self.current_step.screen(self.screen_surface, self.generator.last_photo_bundle))
            if self.generator.last_photo_bundle and self.current_step.transform_result_size:
                self.process_image()
                self.generator.last_photo_bundle = None
        return self.current_step

    def process_image(self):
        self.processor.dual_single_image(self.generator.last_photo_bundle).save(
            self.generator.last_photo_bundle.processed)
        self.print_image()

    def print_image(self):
        photo_name = self.generator.last_photo_bundle.processed
        command = string.Template(print_command).safe_substitute(filename=photo_name)
        print("executing: '%s'" % command)
        subprocess.call(command.split(' '))

    def paint(self, screen):
        self.screen.blit(screen, (0, 0))
        pygame.display.flip()


class ResultArea:
    area = None
    mid_point = None
    size = None
    bounds = None

    def __init__(self, area):
        self.area = area
        print("_RESULT_AREA: %s,%s,%s,%s" % self.area)
        self.size = (self.area[2] - self.area[0], self.area[3] - self.area[1])
        print("_RESULT_AREASIZE: %s,%s" % self.size)
        self.bounds = (self.area[0], self.area[1], self.size[0], self.size[1])
        self.mid_point = (self.area[0] + self.size[0] / 2, self.area[1] + self.size[1] / 2)
        print("_RESULT_AREA_MID_POINT: %s,%s" % self.mid_point)

    def size_for_screen(self, images):
        image_width = images[0][1].width
        image_height = images[0][1].height
        x_ratio = float(self.size[0]) / image_width
        y_ratio = float(self.size[1]) / (image_height * len(images))
        print("x/y ratio: %s/%s" % (x_ratio, y_ratio))
        if x_ratio < y_ratio:
            return int(image_width * x_ratio), int(image_height * x_ratio)
        else:
            return int(image_width * y_ratio), int(image_height * y_ratio)


class Step:
    start_time = 0
    image = None
    click_transitions = []
    time_transition = None
    event_transitions = []
    command = None
    command_running = False
    result_area = False
    transform_result_size = None

    def __init__(self, image_name, click_transitions=None, time_transition=None, event_transitions=None, command=None,
                 result=False):
        self.start_time = 0
        if image_name:
            self.image, singleRect = load_image(image_name, style=args.style)
        self.click_transitions = click_transitions
        self.time_transition = time_transition
        self.event_transitions = event_transitions
        self.command = command
        if result:
            self.result_area = ResultArea(RES_AREA)

    def screen(self, surface, last_photo_bundle):
        surface.fill(_WHITE)
        if self.image:
            surface.blit(pygame.transform.scale(self.image, SIZE), (0, 0))
        if args.test_click_area and self.click_transitions:
            s = pygame.Surface(surface.get_size())
            s.set_alpha(128)
            s.fill(_WHITE)
            for tran in self.click_transitions:
                pygame.draw.rect(s, _RED, tran[1], 10)
            surface.blit(s, (0, 0))
        if self.is_result_screen():
            images = []
            for image_path in last_photo_bundle.raw:
                images.append(load_image(image_path))
            if not self.transform_result_size:
                self.transform_result_size = self.result_area.size_for_screen(images)
                print("transform_result_size: %s,%s" % (self.transform_result_size[0], self.transform_result_size[1]))
            for index, image in enumerate(images):
                transformed_image = pygame.transform.scale(image[0], self.transform_result_size)
                surface.blit(transformed_image, self.start_cords(images, index))
            if args.test_click_area:
                s = pygame.Surface(surface.get_size())
                s.set_alpha(128)
                s.fill(_WHITE)
                pygame.draw.rect(s, _RED, self.result_area.bounds, 10)
                surface.blit(s, (0, 0))
        return surface

    def is_result_screen(self):
        return self.result_area

    def start_cords(self, images, index):
        return (self.result_area.mid_point[0] - self.transform_result_size[0] / 2, self.result_area.mid_point[1] - (
            self.transform_result_size[1] * (len(images)) / 2) + self.transform_result_size[
                    1] * index)

    def execute(self, game_window):
        next_screen = None
        if self.command and not self.command_running:
            self.command_running = True
            if not args.test_image:
                    photo_name = game_window.generator.last_photo_bundle.preview
                command = string.Template(command).safe_substitute(filename=photo_name)
                print("executing: '%s'" % command)
                subprocess.call(command.split(' '))
            self.command_running = False
            next_screen = self.command[0]
        self.start_time = 0
        return next_screen

    def transition(self, e, game_window):
        if self.command:
            self.start_time = 0
            return self.execute(game_window)
        if self.click_transitions and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for tran in self.click_transitions:
                if tran[1].collidepoint(e.pos):
                    self.start_time = 0
                    if len(tran) > 2:
                        game_window.last_result_image = None
                        game_window.generator.create(tran[2])
                    return tran[0]
        if self.time_transition:
            if e.type == _COUNT_DOWN_EVENT:
                self.start_time += 1
                if self.start_time == self.time_transition[1]:
                    self.start_time = 0
                    return self.time_transition[0]
        return None


args = parser.parse_args()
main_screen = fborx.get_screen(SIZE, args.full_screen)
update_globals(main_screen.get_size())
gw = GameWindow(main_screen)
pygame.time.set_timer(_COUNT_DOWN_EVENT, 1000)
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print event.type
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print event.key
                running = False
        gw.transition(event)
    gw.clock.tick(60)

# make sure to call pygame.quit() if using the framebuffer to get back to your terminal
pygame.quit()
