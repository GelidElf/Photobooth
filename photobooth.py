
import pygame
from pygame.locals import *
import fborx

# this will open a 800x800 window if xserver is running or fullscreen fb if not

backgroundx = 800;
backgroundy = 800;
screen = fborx.getScreen(backgroundx,backgroundy);

# this will draw a red rect
pygame.draw.rect(screen, (255,0,0), Rect(100,100,100,100))

background = pygame.image.load("testImages/maxresdefault.jpg");
screen.blit(background,(0,0));

# this will draw some text with custom font and color
# (I hope the font works for you, windows users may have to change to arial)
'''
myfont = pygame.font.SysFont("monospace", 50)
label = myfont.render("The screen size is " + str(fborx.size[0]) +"x" + str(fborx.size[1]), 1, (0,255,0))
screen.blit(label, (10, 300))
'''

BLACK = (0,0,0);
WHITE = (255,255,255);

# play button
play_big = pygame.draw.rect(screen, BLACK, (backgroundx - 130, backgroundy - 70, 260, 60))
play_outline = pygame.draw.rect(screen, WHITE, (backgroundx - 130, backgroundy - 70, 255, 55))
myfont = pygame.font.SysFont("monospace", 50)
playtext = myfont.render('Play', True, BLACK, None)
playtext_rect = playtext.get_rect()
playtext_rect.centerx = backgroundx
playtext_rect.centery = backgroundy - 50
screen.blit(playtext, playtext_rect)

# now update the display to show the new graphics
pygame.display.flip()

# this code just waits for the ESC key (isn't beauty with the loop, but works for now)
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        if pygame.mouse.get_pressed()[0] == 1:
            if play_big.collidepoint(pygame.mouse.get_pos()):
                print('button pressed')

# make sure to call pygame.quit() if using the framebuffer to get back to your terminal
pygame.quit()
