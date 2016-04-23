import pygame
import os
size = (0, 0)


def get_screen(size, full_screen=False):
                    pygame.init()
                    if 'DISPLAY' in os.environ:
                            try:
                                    display = get_window_display()
                            except:
                                    display = get_fb_display()
                    else:
                            try:
                                    display = get_fb_display()
                            except:
                                    display = get_window_display()
                    screen_size = pygame.display.Info().current_w, pygame.display.Info().current_h

                    print("Original X server size: %dx%d" % screen_size)
                    if full_screen:
                        return display.set_mode(size, pygame.FULLSCREEN)
                    else:
                        print('Resizing to %dx%d' % size)
                        return display.set_mode(size)


def get_window_display():
                    print("Try to open a window")
                    global size
                    return pygame.display


def get_fb_display():
                    print("Try to open Fb")
                    global size
                    disp_no = os.getenv("DISPLAY")
                    print("disp_no " +str(disp_no))
                    if disp_no:
                            print ("I'm running under X display = {0}".format(disp_no))

                    drivers = ['fbturbo', 'fbcon', 'directfb', 'svgalib', 'xvfb', 'x11', 'dga', 'ggi', 'vgl', 'aalib', 'windib', 'directx']
                    # the last 2 are windows where we should not need the fb since it always has desktop, but lets keep them anyway...
                    found = False
                    for driver in drivers:
                            # Make sure that SDL_VIDEODRIVER is set
                            if not os.getenv('SDL_VIDEODRIVER'):
                                    os.putenv('SDL_VIDEODRIVER', driver)
                            try:
                                    print("Driver: "+driver)
                                    pygame.display.init()
                            except pygame.error:
                                    print('Driver: {0} failed.'.format(driver))
                                    continue
                            found = True
                            print("this one works.")
                            break

                    if not found:
                            raise Exception('No suitable video driver found!')

                    return pygame.display
