from unittest import TestCase
from PIL import Image
from green_screen import Chroma
import os

TESTDATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/chroma')

class TestChroma(TestCase):

    def test_alpha_composite(self):
        c = Chroma(Image.open(os.path.join(TESTDATA_PATH+"/background.jpg")))
        res = c.alpha_composite(Image.open(os.path.join(TESTDATA_PATH+"/cromaperson.jpg")))
        res.save(os.path.join(TESTDATA_PATH+"/result.jpg"))
