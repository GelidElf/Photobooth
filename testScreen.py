import os
import pygame
import time
import random
 
class GameWindow :
    screen = None;
    size = None;
    
    def __init__(self,windowSize):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print ("I'm running under X display = {}".format(disp_no))
        
        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                print("Driver: "+driver)
                pygame.display.init()
            except pygame.error:
                print ('Driver: {0} failed.'.format(driver))
                continue
            found = True
            print("this one works.")
            break
    
        if not found:
            raise Exception('No suitable video driver found!')
        
        if not windowSize:
            self.size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        else:
            self.size = windowSize
        print ("Framebuffer size: %d x %d" % (self.size[0], self.size[1]))
        self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))        
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()
 
    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."
 
    def test(self):
        # Fill the screen with red (255, 0, 0)
        red = (255, 0, 0)
        self.screen.fill(red)
        # Update the display
        pygame.display.update()



# Create an instance of the PyScope class
gw = GameWindow()
mms = MainMenuScreen()
mms.paint()
time.sleep(10)
