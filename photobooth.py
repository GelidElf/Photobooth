import argparse

import pygame
import threading

import fborx
from config import current_config
from photo.photo_name_generator import NameGenerator
from processor_pillow import Processor
from window import GameWindow
from app.http_server import app

parser = argparse.ArgumentParser(description='Photobooth.')
parser.add_argument('-f', '--full_screen', action='store_true', default=False)
parser.add_argument('-x', type=int, default=720)
parser.add_argument('-y', type=int, default=576)
parser.add_argument('-s', '--style', default='blanco_negro')
parser.add_argument('-b', '--border', default=0)
parser.add_argument('-tca', '--test_click_area', action='store_true', default=False)
parser.add_argument('-ti', '--test-image', action='store_true', default=False)
parser.add_argument('--logging', action='store_true', default=False)
parser.add_argument('--prefix', default='test_session')
parser.add_argument('--output_path', default=current_config.ROOT_DIR)
parser.add_argument('--process', choices=('single', 'dual', 'dual_sepia', 'four', 'four_album'))
parser.add_argument('-ws', '--web_server', action='store_true', default=False)
parser.add_argument('--win_env', action='store_true', default=False)

args = parser.parse_args()

SIZE = (args.x, args.y)
RES_AREA = None

main_screen = fborx.get_screen(SIZE, args.full_screen)
current_config.update_globals(main_screen.get_size(), args)
generator = NameGenerator(current_config)
if current_config.args.web_server:
    app.config.generator = generator
    app.config.profile = current_config.args.prefix
    t = threading.Thread(target=app.run, args=('0.0.0.0',))
    t.daemon = True
    t.start()
gw = GameWindow(main_screen, generator, Processor(generator.banner_path, current_config.args.process,
                                                  current_config.args.win_env))
pygame.time.set_timer(current_config.COUNT_DOWN_EVENT, 1000)
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if current_config.args.logging:
            print "event %s " % event
        gw.transition(event)
    pygame.event.pump()

# make sure to call pygame.quit() if using the framebuffer to get back to your terminal
pygame.quit()
