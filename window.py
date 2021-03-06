import string
import subprocess
import threading

import pygame

from config import current_config
from step import Step


def start_step():
    if current_config.args.process == 'four':
        return 'multiple1'
    elif current_config.args.process == 'four_album':
        return 'multiple1'
    else:
        return 'single'


def number_of_photos():
    if current_config.args.process == 'four':
        return 4
    elif current_config.args.process == 'four_album':
        return 4
    else:
        return 1


def slide_name(number):
    return 'Slide' + str(number) + '.JPG'


def slide_names(start, number):
    return [slide_name(x) for x in range(start, start + number)]


class GameWindow:
    screen = None
    clock = None
    windows = {}
    current_step = None
    screen_surface = None
    generator = None
    last_result_image = None
    processor = None

    def __init__(self, screen, generator, processor):
        self.test_image = current_config.args.test_image
        self.test_click_area = current_config.args.test_click_area
        self.generator = generator
        self.processor = processor
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.windows["welcome"] = Step(generator.welcome_path, [("menu", pygame.Rect((0, 0), self.screen.get_size()))])
        start_button = pygame.Rect(self.screen.get_size()[0] * 0.25, 0, self.screen.get_size()[0] * 0.5,
                                   self.screen.get_size()[1])
        self.windows["menu"] = Step('Slide2.JPG', [(start_step(), start_button, number_of_photos())])
        self.wait_steps('single', 3, 'process')
        self.windows["process"] = Step('Slide9.JPG', None, ('single-result', 1))
        self.wait_steps('multiple1', 10, 'multiple2')
        self.wait_steps('multiple2', 16, 'multiple3')
        self.wait_steps('multiple3', 22, 'multiple4')
        self.wait_steps('multiple4', 28, 'process')
        return_to_menu = pygame.Rect((0, self.screen.get_size()[1] - 200), (200, self.screen.get_size()[1]))
        print_button = pygame.Rect((0, 0), (200, 200))
        self.windows["single-result"] = Step('Slide35.JPG', [('menu', return_to_menu), ('print', print_button)],
                                             ('welcome', 20), result=True)
        self.windows["print"] = Step('Slide36.JPG', None, command=('print2', 'PRINT'))
        self.windows["print2"] = Step('Slide36.JPG', None, ('menu', 2))

        self.current_step = self.windows['welcome']
        self.screen_surface = pygame.Surface(self.screen.get_size())
        self.paint(
            self.current_step.screen(self.screen_surface, self.generator.last_photo_bundle, self.test_click_area))

    def wait_steps(self, name, first_slide_number, next_step):
        self.windows[name] = Step(slide_names(first_slide_number, 5), None, (name + 'smile', 1))
        self.windows[name + "smile"] = Step(slide_name(first_slide_number + 5), None, command=(next_step, "PHOTO"))

    def transition(self, e):
        next_window_name = self.current_step.transition(e, self)
        if next_window_name:
            if next_window_name != "revisit_step":
                self.current_step = self.windows[next_window_name]
                print ("in step %s" % next_window_name)
            self.paint(
                self.current_step.screen(self.screen_surface, self.generator.last_photo_bundle, self.test_click_area))
            if self.generator.last_photo_bundle and self.current_step.transform_result_size:
                self.process_image()
        return self.current_step

    def process_image(self):
        if current_config.args.thread_processing:
            t = threading.Thread(target=self.processor.process_image,
                                 args=(self.generator.last_photo_bundle, current_config.args.web_server,))
            t.daemon = True
            t.start()
        else:
            self.processor.process_image(self.generator.last_photo_bundle, current_config.args.web_server)

    def take_photo(self):
        photo_name = self.generator.raw_queue.pop()
        if current_config.args.win_env:
            photo_name = str.replace(photo_name, r'\\', r'\\\\')
            print("win_filename: '%s'" % photo_name)
        command = string.Template(self.processor.photo_capture_command).safe_substitute(filename=photo_name)
        print("executing: '%s'" % command)
        if not self.test_image:
            subprocess.call(command.split(' '))

    def paint(self, screen):
        self.screen.blit(screen, (0, 0))
        pygame.display.flip()
