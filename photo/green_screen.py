from PIL import Image
import numpy as np
import cv2


class Chroma:
    """
    Trying the HSV method
    """
    background_image = None

    def __init__(self, background_image):
        self.background_image = background_image


    def _crop_background_image(self):
        pass

    def merge(self, img):
        height, width, _ = self.background_image.shape
        cv2.resize(img, (height, width))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_green = np.array([20, 60, 0])
        upper_green = np.array([80, 255, 255])
        mask = cv2.bitwise_not(cv2.inRange(hsv, lower_green, upper_green))

        # kernel = np.ones((5, 5),'int')
        # dilated = cv2.dilate(mask, kernel)

        #res = cv2.bitwise_and(img, img, mask=mask)
        idx = (mask != 0)
        res = self.background_image.copy()
        res[idx] = img[idx]
        return res
"""
        matte = self.hueDistance(color=cv2.Color.GREEN, minvalue = 40).binarize()
        result = (img-matte)+(self.background_image-matte.invert())
        result.save('result.png')

    def hueDistance(self, img, color=cv2.BLACK, minsaturation=20, minvalue=20, maxvalue=255):

        if isinstance(color, (float, int, long, complex)):
            color_hue = color
        else:
            color_hue = cv2.Color.hsv(color)[0]

        vsh_matrix = self.toHSV().getNumpy().reshape(-1, 3)  # again, gets transposed to vsh
        hue_channel = np.cast['int'](vsh_matrix[:, 2])

        if color_hue < 90:
            hue_loop = 180
        else:
            hue_loop = -180
        # set whether we need to move back or forward on the hue circle

        distances = np.minimum(np.abs(hue_channel - color_hue), np.abs(hue_channel - (color_hue + hue_loop)))
        # take the minimum distance for each pixel

        distances = np.where(
            np.logical_and(vsh_matrix[:, 0] > minvalue, vsh_matrix[:, 1] > minsaturation),
            distances * (255.0 / 90.0),  # normalize 0 - 90 -> 0 - 255
            255.0)  # use the maxvalue if it false outside of our value/saturation tolerances

        return Image(distances.reshape(self.width, self.height))
"""