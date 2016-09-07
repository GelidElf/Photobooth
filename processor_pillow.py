import os
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw


class ProcessType:
    Single = 'single'
    Dual = 'dual'
    Two = 'two'
    Four = 'four'
    FourAlbum = 'four_album'


class Processor:
    banner = None
    esif_logo = None
    resized_from = None
    mode = None

    def __init__(self, banner_path, mode=ProcessType.Dual):
        self.banner = Image.open(banner_path)
        self.esif_logo = Image.open(os.path.join(os.path.dirname(__file__), "images/logo_esif.png"))
        self.mode = mode
        print("banner", self.banner.format, self.banner.size, self.banner.mode)

    def process_image(self, photo_bundle):
        parent_dir = os.path.dirname(photo_bundle.processed)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        if self.mode == ProcessType.Single:
            return self.process_single_image(photo_bundle).save(photo_bundle.processed)
        elif self.mode == ProcessType.Dual:
            return self.process_dual_image(photo_bundle).save(photo_bundle.processed)
        elif self.mode == ProcessType.Two:
            return self.process_two_images(photo_bundle).save(photo_bundle.processed)
        elif self.mode == ProcessType.Four:
            return self.process_four_images(photo_bundle).save(photo_bundle.processed)
        elif self.mode == ProcessType.FourAlbum:
            return self.process_four_album_images(photo_bundle).save(photo_bundle.processed)

    def process_four_images(self, photo_bundle):
        images = map(lambda image: Image.open(image), photo_bundle.raw)
        new_size = map(lambda x: int(x * 0.5), images[0].size)
        map(lambda x: x.thumbnail(new_size, Image.ANTIALIAS), images)
        im = images[0]
        self.resize_additions(im)
        print("image", im.format, im.size, im.mode)
        new_height = int((im.size[1]*2 + self.banner.size[1]) * 1.10)
        new_width = int((new_height / 1.45) * 2)
        top_border = int(new_height / 20)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        banner_x_start = int(new_width / 2 - self.banner.size[0] / 2)
        new_im.paste(self.banner, (banner_x_start, top_border + im.size[1]))
        left_x_start = int(new_width / 4 - im.size[0] / 2)
        right_x_start = int(new_width / 2 + left_x_start)
        new_im.paste(images[0], (left_x_start, top_border))
        new_im.paste(images[1], (right_x_start, top_border))
        new_im.paste(images[2], (left_x_start, top_border + im.size[1] + self.banner.size[1]))
        new_im.paste(images[3], (right_x_start, top_border + im.size[1] + self.banner.size[1]))
        esif_logo_x_start = int(new_width - left_x_start - self.esif_logo.size[0])
        esif_logo_y_start = int((new_height - self.esif_logo.size[1])/2)
        new_im.paste(self.esif_logo, (esif_logo_x_start, esif_logo_y_start), mask=self.esif_logo)
        return new_im

    def process_four_album_images(self, photo_bundle):
        images = map(lambda image: Image.open(image), photo_bundle.raw)
        new_size = map(lambda x: int(x * 0.5), images[0].size)
        map(lambda x: x.thumbnail(new_size, Image.ANTIALIAS), images)
        im = images[0]
        self.resize_additions(im)
        print("image", im.format, im.size, im.mode)
        new_height = int((im.size[1] + self.banner.size[1]) * 1.15) * 2
        new_width = int((new_height / 1.45) * 2)
        top_border = int(new_height / 20)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        left_x_center = int(new_width / 4)
        right_x_center = int(new_width / 2 + left_x_center)
        row_rop_start = top_border
        row_bottom_start = int(new_height / 2)

        image_width = im.size[0]
        image_height = im.size[1]
        banner_width = self.banner.size[0]
        banner_height = self.banner.size[1]

        esif_logo_left_x = left_x_center + (image_width / 2) - self.esif_logo.size[0]
        esif_logo_right_x = right_x_center + (image_width / 2) - self.esif_logo.size[0]

        new_im.paste(images[0], (left_x_center - (image_width / 2), row_rop_start))
        new_im.paste(self.banner, (left_x_center - (banner_width / 2), row_rop_start + image_height))
        new_im.paste(self.esif_logo, (esif_logo_left_x, row_rop_start + image_height), mask=self.esif_logo)

        new_im.paste(images[1], (right_x_center - (image_width / 2), row_rop_start))
        new_im.paste(self.banner, (right_x_center - (banner_width / 2), row_rop_start + image_height))
        new_im.paste(self.esif_logo, (esif_logo_right_x, row_rop_start + image_height), mask=self.esif_logo)

        new_im.paste(images[2], (left_x_center - (image_width / 2), row_bottom_start))
        new_im.paste(self.banner, (left_x_center - (banner_width / 2), row_bottom_start + image_height))
        new_im.paste(self.esif_logo, (esif_logo_left_x, row_bottom_start + image_height), mask=self.esif_logo)

        new_im.paste(images[3], (right_x_center - (image_width / 2), row_bottom_start))
        new_im.paste(self.banner, (right_x_center - (banner_width / 2), row_bottom_start + image_height))
        new_im.paste(self.esif_logo, (esif_logo_right_x, row_bottom_start + image_height), mask=self.esif_logo)

        return new_im

    def process_dual_image(self, photo_bundle):
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
        draw.line((0, line_y, new_width, line_y), fill=128, width=0)
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
        im.thumbnail(map(lambda x: int(x * 0.5), im.size), Image.ANTIALIAS)
        self.resize_additions(im)
        print("image", im.format, im.size, im.mode)
        new_height = int((im.size[1] + self.banner.size[1]) * 1.05)
        new_width = int(new_height * 1.5)
        top_border = int(new_height / 20)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        banner_x_start = int(new_width / 2 - self.banner.size[0] / 2)
        new_im.paste(self.banner, (banner_x_start, top_border + im.size[1]))
        im_x_start = int(new_width / 2 - im.size[0] / 2)
        new_im.paste(im, (im_x_start, top_border))
        esif_logo_x_start = int(new_width - im_x_start - self.esif_logo.size[0])
        esif_logo_y_start = int(top_border + im.size[1])
        new_im.paste(self.esif_logo, (esif_logo_x_start, esif_logo_y_start), mask=self.esif_logo)
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
        ratio = (im.size[1] * 0.1) / self.esif_logo.size[1]
        size = map(lambda x: int(x * ratio), self.esif_logo.size)
        if self.esif_logo.size != size:
            self.esif_logo = self.esif_logo.resize(size, Image.BICUBIC)
        print "new banner size %sx%s" % self.esif_logo.size
