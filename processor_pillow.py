import os
from PIL import Image
from PIL import ImageColor


class Processor:
    banner = None
    resized_from = None

    def __init__(self, banner_path):
        self.banner = Image.open(banner_path)
        print("banner", self.banner.format, self.banner.size, self.banner.mode)

    def process_image(self, photo_bundle):
        items = len(photo_bundle.raw)
        parent_dir = os.path.dirname(photo_bundle.processed)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        if items == 0:
            print("ERROR")
        elif items == 1:
            self.process_single_image(photo_bundle).save(photo_bundle.processed)
        elif items == 2:
            self.process_two_images(photo_bundle).save(photo_bundle.processed)

    def dual_single_image(self, photo_bundle):
        im = Image.open(photo_bundle.raw[0])
        im.thumbnail(map(lambda x: int(x * 0.5), im.size), Image.ANTIALIAS)
        self.resize_banner_to_image(im)
        print("image", im.format, im.size, im.mode)
        new_height = int((im.size[1] + self.banner.size[1]) * 1.05) * 2
        new_width = int(new_height / 1.46)
        top_border = int(new_height / 40)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        banner_x_start = int(new_width / 2 - self.banner.size[0] / 2)
        new_im.paste(self.banner, (banner_x_start, new_height - self.banner.size[1]))
        new_im.paste(self.banner, (banner_x_start, new_height/2 - self.banner.size[1]))
        im_x_start = int(new_width / 2 - im.size[0] / 2)
        new_im.paste(im, (im_x_start, top_border))
        new_im.paste(im, (im_x_start, top_border+new_height/2))
        return new_im

    def process_single_image(self, photo_bundle):
        im = Image.open(photo_bundle.raw[0])
        print("image", im.format, im.size, im.mode)

        new_height = int((im.size[1] + self.banner.size[1]) * 1.05)
        new_width = int(new_height * 1.5)
        top_border = int(new_height / 20)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        new_im.paste(self.banner, (int(new_width / 2 - self.banner.size[0] / 2), new_height - self.banner.size[1]))
        new_im.paste(im, (int(new_width / 2 - im.size[0] / 2), top_border))
        return new_im

    def process_two_images(self, photo_bundle):
        im1 = Image.open(photo_bundle.raw[0])
        resize = (im1.size[0] * 0.6, im1.size[1] * 0.6)
        im1.thumbnail(resize, Image.ANTIALIAS)

        new_width = int(im1.size[0] * 10 / 9)
        new_height = int(new_width * 1.5)

        print("image", im1.format, im1.size, im1.mode)
        im2 = Image.open(photo_bundle.raw[1])
        im2.thumbnail(resize, Image.ANTIALIAS)
        print("image", im2.format, im2.size, im2.mode)

        top_border = int(new_height / 20)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        new_im.paste(im1, (int(new_width / 2 - im1.size[0] / 2), top_border))
        new_im.paste(im2, (int(new_width / 2 - im2.size[0] / 2), new_height - im2.size[1] - self.banner.size[1]))
        new_im.paste(self.banner, (int(new_width / 2 - self.banner.size[0] / 2), new_height - self.banner.size[1]))
        return new_im

    def resize_banner_to_image(self, im):
        if self.resized_from != im.size:
            print "old banner size %sx%s" % self.banner.size
            banner_ratio = (im.size[1] * 0.25) / self.banner.size[1]
            banner_size = map(lambda x: int(x * banner_ratio), self.banner.size)
            if self.banner != banner_size:
                self.banner = self.banner.resize(banner_size, Image.BICUBIC)
                self.resized_from = im.size
            print "new banner size %sx%s" % self.banner.size
