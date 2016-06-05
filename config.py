import os

import pygame


class Config:
    ROOT_DIR = os.path.dirname(__file__)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    COUNT_DOWN_EVENT = pygame.USEREVENT + 1
    EXPECTED_RESOLUTION = (800, 480)
    EXT = ".jpg"
    RES_AREA = None
    SIZE = None
    args = None

    def __init__(self):
        self.ROOT_DIR = os.path.dirname(__file__)
        print "ROOT DIR %s" % self.ROOT_DIR

    def update_globals(self, size, args):
        self.args = args
        self.SIZE = size
        res_cx = (float(self.SIZE[0]) / self.EXPECTED_RESOLUTION[0], float(self.SIZE[1]) / self.EXPECTED_RESOLUTION[1])
        print("res_cx: %s,%s" % res_cx)
        border = (30 * res_cx[0])
        self.RES_AREA = (198 * res_cx[0], border, self.SIZE[0] - border, self.SIZE[1] - border)
        print("RES_AREA: %s,%s,%s,%s" % self.RES_AREA)


current_config = Config()
