from unittest import TestCase
from PIL import Image
from green_screen import Chroma
import os
import cv2

TESTDATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/chroma')

class TestChroma(TestCase):

    image = None

    def test_merge(self):
        c = Chroma(cv2.imread(os.path.join(TESTDATA_PATH+"/background.jpg")))
        self.image = cv2.imread(os.path.join(TESTDATA_PATH+"/cromaperson.jpg"))
        res = c.merge(self.image)
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.get_values)
        while True:
            cv2.imshow('image', self.image)
            cv2.imshow('frame', res)

            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break
        cv2.destroyAllWindows()


    # mouse callback function
    def get_values(self, event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print y,x,self.image[y][x]

