import os
from PIL import Image
from PIL import ImageColor


class Processor:

    def process_image(self, last):
        items = len(last.raw)
        if items == 0:
            print ("ERROR")
        elif items == 1:
            self.process_single_image(last)
        elif items == 2:
            self.process_two_images(last)

    def process_single_image (self, images):
        banner_path = 'images/banner.jpg'
        banner = Image.open(banner_path)
        print("banner", banner.format, banner.size, banner.mode)
        im = Image.open(images.raw[0])
        print("image", im.format, im.size, im.mode)

        new_height = int(im.size[1] * 1.25)
        new_width = int(new_height * 1.5)
        top_border = int(new_height/20)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        new_im.paste(im, (int(new_width/2 - im.size[0]/2), top_border))
        new_im.paste(banner, (int(new_width/2 - banner.size[0]/2), new_height-banner.size[1]))
        processed_path = images.processed
        parent_dir = os.path.dirname(processed_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        new_im.save(processed_path)

    def process_two_images (self, images):
        banner_path = 'images/banner.jpg'
        banner = Image.open(banner_path)
        print("banner", banner.format, banner.size, banner.mode)
        im1 = Image.open(images.raw[0])
        resize = (im1.size[0]*0.6, im1.size[1]*0.6)
        im1.thumbnail(resize, Image.ANTIALIAS)

        new_width = int(im1.size[0] * 10/9)
        new_height = int(new_width * 1.5)

        print("image", im1.format, im1.size, im1.mode)
        im2 = Image.open(images.raw[1])
        im2.thumbnail(resize, Image.ANTIALIAS)
        print("image", im2.format, im2.size, im2.mode)

        top_border = int(new_height/20)
        print("new", new_width, new_height, top_border)

        new_im = Image.new('RGBA', (new_width, new_height), ImageColor.getcolor('WHITE', 'RGBA'))
        new_im.paste(im1, (int(new_width/2 - im1.size[0]/2), top_border))
        new_im.paste(im2, (int(new_width/2 - im2.size[0]/2), new_height-im2.size[1]-banner.size[1]))
        new_im.paste(banner, (int(new_width/2 - banner.size[0]/2), new_height-banner.size[1]))
        processed_path = images.processed
        parent_dir = os.path.dirname(processed_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        new_im.save(processed_path)
