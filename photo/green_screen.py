from PIL import Image
import numpy as np
import cv2


class Chroma:
    background_image = None
    reference_image = None
    thresh = None
    use_edges = True
    bg_edges = None

    def __init__(self, reference_image, background_image, thresh):
        self.background_image = background_image
        self.reference_image = reference_image
        self.thresh = thresh

        # this is for automatically setting corners of frame to background
        gray_shape = (reference_image.shape[0], reference_image.shape[1])
        bg_edges = np.zeros(gray_shape, np.uint8)
        # storage format is y,x, color
        edge_size_x = bg_edges.shape[1] / 8
        edge_size_y = bg_edges.shape[0] / 4
        bg_edges[0:edge_size_y, 0:edge_size_x] = 255
        bg_edges[0:edge_size_y, -edge_size_x:] = 255
        bg_edges[-edge_size_y:, 0:edge_size_x] = 255
        bg_edges[-edge_size_y:, -edge_size_x:] = 255
        self.bg_edges = bg_edges

    def _crop_background_image(self):
        pass

    def merge(self, img):
        use_denoise = False
        denoise_h = 0
        fgmask = self.find_fgmask(img, self.reference_image, thresh=self.thresh, use_denoise=use_denoise, h=denoise_h)
        bgmask = cv2.bitwise_not(fgmask)

        if self.use_edges:
            bgmask = cv2.bitwise_or(bgmask, self.bg_edges)
            fgmask = cv2.bitwise_not(bgmask)

        fgimg = cv2.bitwise_and(img, img, mask=fgmask)
        bgimg = cv2.bitwise_and(self.background_image, self.background_image, mask=bgmask)

        sum = cv2.add(fgimg, bgimg)
        result = sum

    '''
    find_fgmask: Finds the 'foregound mask', i.e. where the foreground objects are
    Author: Scott Hawley
    It doesn't use any especially clever algorithm (e.g., no BGMOG), just the fruits
    of significant trial-and-error on my part, for what seems to work best

    Warning: de-noising is slow, and best suited for post-processing only
    '''

    def find_fgmask(self, img, ref_img=self.background_image, thresh=13.0, use_denoise=False, h=10.0):
        diff1 = cv2.subtract(img, ref_img)
        diff2 = cv2.subtract(ref_img, img)
        diff = diff1 + diff2

        sws = int(np.ceil(21 * h / 10) // 2 * 2 + 1)
        diff[abs(diff) < thresh] = 0
        gray = cv2.cvtColor(diff.astype(np.uint8), cv2.COLOR_BGR2GRAY)
        gray[np.abs(gray) < 10] = 0
        if use_denoise:
            cv2.fastNlMeansDenoising(gray, gray, h=h, templateWindowSize=5, searchWindowSize=sws)
        fgmask = gray.astype(np.uint8)
        fgmask[fgmask > 0] = 255
        return fgmask


