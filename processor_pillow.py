import os
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw


class Processor:
    banner = None
    esif_logo = None
    resized_from = None

    def __init__(self, banner_path):
        self.banner = Image.open(banner_path)
        self.esif_logo = Image.open(os.path.join(os.path.dirname(__file__), "images/logo_esif.png"))
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
        self.resize_additions(im)
        print("image", im.format, im.size, im.mode)
        new_height = int((im.size[1] + self.banner.size[1]) * 1.15) * 2
        new_width = int(new_height / 1.45)
        top_border = int(new_height / 20)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        draw = ImageDraw.Draw(new_im)
        line_y = top_border + im.size[1] + self.banner.size[1]
        draw.line((0,line_y,new_width,line_y), fill=128, width=0)
        banner_x_start = int(new_width / 2 - self.banner.size[0] / 2)
        new_im.paste(self.banner, (banner_x_start, top_border + im.size[1]))
        new_im.paste(self.banner, (banner_x_start, int(top_border * 1.5) + im.size[1] * 2 + self.banner.size[1]))
        im_x_start = int(new_width / 2 - im.size[0] / 2)
        new_im.paste(im, (im_x_start, top_border))
        new_im.paste(im, (im_x_start, int(top_border * 1.5) + im.size[1] + self.banner.size[1]))
        esif_logo_x_start = int(new_width - im_x_start - self.esif_logo.size[0])
        esif_logo_y_start = int(top_border + im.size[1])
        new_im.paste(self.esif_logo, (esif_logo_x_start, esif_logo_y_start), mask=self.esif_logo)
        new_im.paste(self.esif_logo, (esif_logo_x_start, int(top_border * 1.5) + (im.size[1]*2) + self.banner.size[1]), mask=self.esif_logo)
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

    def resize_additions(self, im):
        if self.resized_from != im.size:
            self.resize_banner_to_image(im)
            self.resize_esif_logo_to_image(im)
            self.resized_from = im.size

    def resize_banner_to_image(self, im):
        print "old banner size %sx%s" % self.banner.size
        banner_ratio = (im.size[1] * 0.25) / self.banner.size[1]
        banner_size = map(lambda x: int(x * banner_ratio), self.banner.size)
        if self.banner.size != banner_size:
            self.banner = self.banner.resize(banner_size, Image.BICUBIC)
        print "new banner size %sx%s" % self.banner.size

    def resize_esif_logo_to_image(self, im):
        print "old banner size %sx%s" % self.esif_logo.size
        ratio = (im.size[1] * 0.125) / self.esif_logo.size[1]
        size = map(lambda x: int(x * ratio), self.esif_logo.size)
        if self.esif_logo.size != size:
            self.esif_logo = self.esif_logo.resize(size, Image.BICUBIC)
        print "new banner size %sx%s" % self.esif_logo.size
