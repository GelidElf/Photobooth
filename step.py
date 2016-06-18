import pygame
import os

from config import current_config
from utils import load_image


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
            if os.path.exists(image_name):
                self.image, singleRect = load_image(image_name)
            else:
                self.image, singleRect = load_image(image_name, style=current_config.args.style)
        self.click_transitions = click_transitions
        self.time_transition = time_transition
        self.event_transitions = event_transitions
        self.command = command
        if result:
            self.result_area = ResultArea(current_config.RES_AREA)

    def screen(self, surface, last_photo_bundle, test_click_area):
        surface.fill(current_config.WHITE)
        if self.image:
            surface.blit(pygame.transform.scale(self.image, current_config.SIZE), (0, 0))
        if test_click_area and self.click_transitions:
            s = pygame.Surface(surface.get_size())
            s.set_alpha(128)
            s.fill(current_config.WHITE)
            for tran in self.click_transitions:
                pygame.draw.rect(s, current_config.RED, tran[1], 10)
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
            if test_click_area:
                s = pygame.Surface(surface.get_size())
                s.set_alpha(128)
                s.fill(current_config.WHITE)
                pygame.draw.rect(s, current_config.RED, self.result_area.bounds, 10)
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
            action_type = self.command[1]
            if "PHOTO" == action_type:
                game_window.take_photo()
            elif 'PRINT' == action_type:
                game_window.print_image()
            self.command_running = False
            next_screen = self.command[0]
        self.start_time = 0
        return next_screen

    def transition(self, e, game_window):
        next_screen = None
        if self.command:
            self.start_time = 0
            next_screen = self.execute(game_window)
        elif self.click_transitions and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for tran in self.click_transitions:
                if tran[1].collidepoint(e.pos):
                    self.start_time = 0
                    if len(tran) > 2:
                        game_window.last_result_image = None
                        game_window.generator.create(tran[2])
                    next_screen = tran[0]
        elif self.time_transition:
            if e.type == current_config.COUNT_DOWN_EVENT:
                self.start_time += 1
                if self.start_time == self.time_transition[1]:
                    self.start_time = 0
                    next_screen = self.time_transition[0]
        return next_screen


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