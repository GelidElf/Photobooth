import os

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageOps

gphoto_command = 'gphoto2 --capture-image-and-download --filename ${filename} --force-overwrite'
digicamcontrol_command = 'C:\Program Files (x86)\digiCamControl\\CameraControlCmd.exe /capture  /filename ${filename} '


class ProcessType:
    Single = 'single'
    Dual = 'dual'
    DualSepia = 'dual_sepia'
    Two = 'two'
    Double = 'double'
    Four = 'four'
    FourAlbum = 'four_album'


class Processor:
    banner = None
    esif_logo = None
    resized_from = None
    mode = None
    photo_capture_command = None

    def __init__(self, banner_path, mode=ProcessType.Dual, win_env=False):
        self.banner = Image.open(banner_path)
        self.esif_logo = Image.open(os.path.join(os.path.dirname(__file__), "images/logo_esif.png"))
        self.mode = mode
        if not win_env:
            self.photo_capture_command=gphoto_command
        else:
            self.photo_capture_command=digicamcontrol_command
        print("banner", self.banner.format, self.banner.size, self.banner.mode)

    def process_image(self, photo_bundle, save_for_web):
        processed_image = None
        parent_dir = os.path.dirname(photo_bundle.processed)
        images = self.resize_for_processing(photo_bundle)

        if save_for_web:
            self.create_web_copies(images, photo_bundle)

        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        if self.mode == ProcessType.Single:
            processed_image = self.process_single_image(images)
        elif self.mode == ProcessType.Dual:
            processed_image = self.process_one_in_two(images)
        elif self.mode == ProcessType.DualSepia:
            processed_image = self.process_sepia(self.process_one_in_two(images))
        elif self.mode == ProcessType.Two:
            processed_image = self.process_two_in_one(images)
        elif self.mode == ProcessType.Double:
            processed_image = self.process_two_in_two(images)
        elif self.mode == ProcessType.Four:
            processed_image = self.process_four_images(images)
        elif self.mode == ProcessType.FourAlbum:
            processed_image = self.process_four_album_images(images)

        return processed_image.save(photo_bundle.processed)

    def create_web_copies(self, images, photo_bundle):
        web_images = map(lambda i: i.copy(), images)
        self.shrink_to_half(web_images)
        for index, image in enumerate(web_images):
            image.save(photo_bundle.web[index])

    def resize_for_processing(self, photo_bundle):
        images = map(lambda image: Image.open(image), photo_bundle.raw)
        self.shrink_to_half(images)
        return images

    def shrink_to_half(self, images):
        new_size = map(lambda x: int(x * 0.5), images[0].size)
        map(lambda x: x.thumbnail(new_size, Image.ANTIALIAS), images)

    def process_four_images(self, images):
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

    def process_four_album_images(self, images):
        im = images[0]
        self.resize_additions(im)
        print("image", im.format, im.size, im.mode)
        new_height = int((im.size[1] + self.banner.size[1]) * 1.20) * 2
        new_width = int(new_height * 1.5)
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

    def process_one_in_two(self, images):
        im = images[0]
        self.resize_additions(im)
        print("image", im.format, im.size, im.mode)
        new_height = int((im.size[1] + self.banner.size[1]) * 1.15) * 2
        new_width = int(new_height / 1.45)
        top_border = int(new_height / 20)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGB', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGB'))
        draw = ImageDraw.Draw(new_im)
        line_y = top_border + im.size[1] + self.banner.size[1]
        line_color = ImageColor.getcolor('BLACK', 'RGB')
        draw.rectangle((0, line_y-1, new_width, line_y+1), outline=line_color, fill=line_color)
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

    def process_two_in_two(self, images):
        im1 = images[0]
        self.resize_additions(im1)
        print("image", im1.format, im1.size, im1.mode)
        im2 = images[1]
        new_height = int((im1.size[1] + self.banner.size[1]) * 1.15) * 2
        new_width = int(new_height / 1.45)
        top_border = int(new_height / 20)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        draw = ImageDraw.Draw(new_im)
        line_y = top_border + im1.size[1] + self.banner.size[1]
        line_color = ImageColor.getcolor('BLACK', 'RGBA')
        draw.rectangle((0, line_y-1, new_width, line_y+1), outline=line_color, fill=line_color)
        banner_x_start = int(new_width / 2 - self.banner.size[0] / 2)
        new_im.paste(self.banner, (banner_x_start, top_border + im1.size[1]))
        new_im.paste(self.banner, (banner_x_start, int(top_border * 1.5) + im1.size[1] * 2 + self.banner.size[1]))
        im_x_start = int(new_width / 2 - im1.size[0] / 2)
        new_im.paste(im1, (im_x_start, top_border))
        new_im.paste(im2, (im_x_start, int(top_border * 1.5) + im1.size[1] + self.banner.size[1]))
        esif_logo_x_start = int(new_width - im_x_start - self.esif_logo.size[0])
        esif_logo_y_start = int(top_border + im1.size[1])
        new_im.paste(self.esif_logo, (esif_logo_x_start, esif_logo_y_start), mask=self.esif_logo)
        new_im.paste(self.esif_logo, (esif_logo_x_start, int(top_border * 1.5) + (im1.size[1]*2) + self.banner.size[1]), mask=self.esif_logo)
        return new_im

    def process_single_image(self, images):
        im = images[0]
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

    def process_two_in_one(self, images):
        im1 = images[0]

        new_width = int(im1.size[0] * 10 / 9)
        new_height = int(new_width * 1.5)

        print("image", im1.format, im1.size, im1.mode)
        im2 = images[1]
        print("image", im2.format, im2.size, im2.mode)

        top_border = int(new_height / 20)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        new_im.paste(im1, (int(new_width / 2 - im1.size[0] / 2), top_border))
        new_im.paste(im2, (int(new_width / 2 - im2.size[0] / 2), new_height - im2.size[1] - self.banner.size[1]))
        new_im.paste(self.banner, (int(new_width / 2 - self.banner.size[0] / 2), new_height - self.banner.size[1]))
        return new_im

    def process_sepia(self, im):

        # make sepia ramp (tweak color as necessary)
        sepia = self.make_linear_ramp((255, 240, 192))

        # convert to grayscale
        if im.mode != "L":
            im = im.convert("L")

        # optional: apply contrast enhancement here, e.g.
        im = ImageOps.autocontrast(im)

        # apply sepia palette
        im.putpalette(sepia)

        # convert back to RGB so we can save it as JPEG
        # (alternatively, save it in PNG or similar)
        return im.convert("RGB")

    def make_linear_ramp(self, white):
        # putpalette expects [r,g,b,r,g,b,...]
        ramp = []
        r, g, b = white
        for i in range(255):
            ramp.extend((r * i / 255, g * i / 255, b * i / 255))
        return ramp

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
        print "old esif logo size %sx%s" % self.esif_logo.size
        ratio = (im.size[1] * 0.1) / self.esif_logo.size[1]
        size = map(lambda x: int(x * ratio), self.esif_logo.size)
        if self.esif_logo.size != size:
            self.esif_logo = self.esif_logo.resize(size, Image.BICUBIC)
        print "new esif logo size %sx%s" % self.esif_logo.size
