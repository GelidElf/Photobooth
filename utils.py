import os

import pygame

from config import current_config


def load_image(name, style=None):
    if not style:
        if os.path.isabs(name):
            fullname = name
        else:
            fullname = os.path.join(name)
    else:
        fullname = os.path.join(current_config.ROOT_DIR, 'images', style, name)
    print("image: \"%s\"" % fullname)
    image = pygame.image.load(fullname).convert()
    return image, image.get_rect()