import pygame
import os
size = (0, 0)

#x and y will be the windowsize if an xserver is running
def getScreen(size):
                    pygame.init()
                    display = None
                    if size:
                        print("Original X server size: %d x %d" % (size[0], size[1]))
                    if 'DISPLAY' in os.environ:
                            try:
                                    display = getWindowDisplay()
                            except:
                                    display = getFbDisplay()
                    else:
                            try:
                                    display =  getFbDisplay()
                            except:
                                    display =  getWindowDisplay()
                    if not size:
                            size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
                    print('Resizing to %sx%s' % (size))
                    return display.set_mode(size,pygame.FULLSCREEN),size

def getWindowDisplay():
                    print("Try to open a window")
                    global size
                    return pygame.display
def getFbDisplay():
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

                    return(pygame.display)
