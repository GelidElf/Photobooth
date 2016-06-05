import os

from photo_bundle import PhotoBundle


class NameGenerator:
    prefix = None
    photo_count = None
    raw_path = None
    preview_path = None
    last_photo_bundle = None
    banner_path = None
    raw_queue = None
    status_file = None
    root_dir = None
    ext = None
    test_image = False

    def __init__(self, current_config):
        self.prefix = current_config.args.prefix
        self.test_image = current_config.args.test_image
        self.root_dir = current_config.ROOT_DIR
        self.ext = current_config.EXT
        output_path = current_config.args.output_path
        session_path = os.path.join(output_path, self.prefix)
        if not os.path.exists(session_path):
            os.makedirs(session_path)
            print "ERROR: Session path '%s' created, Move the banner to the path" % session_path
            exit (0)
        self.banner_path = os.path.join(session_path, 'banner.jpg')
        self.raw_path = os.path.join(session_path, "raw")
        if not os.path.exists(self.raw_path):
            os.makedirs(self.raw_path)
        self.preview_path = os.path.join(session_path, "preview")
        if not os.path.exists(self.preview_path):
            os.makedirs(self.preview_path)
        self.raw_queue = []
        self.status_file_name = os.path.join(session_path, "status.txt")
        self.read_photo_counter()

    def create(self, number_photos=1):
        self.raw_queue = []
        if self.test_image:
            for _ in range(number_photos):
                self.photo_count += 1
                self.raw_queue.append(os.path.abspath(os.path.join(self.root_dir, 'images/maxresdefault.jpg')))
            processed = os.path.abspath(os.path.join(self.root_dir, 'images/maxresdefault-processed%s.jpg' % self.photo_count))
        else:
            for _ in range(number_photos):
                self.photo_count += 1
                photo_name = "%s-%s%s" % (self.prefix, self.photo_count, self.ext)
                self.raw_queue.append(os.path.abspath(os.path.join(self.raw_path, photo_name)))
            processed = os.path.abspath(os.path.join(self.preview_path, photo_name))
        self.last_photo_bundle = PhotoBundle(list(self.raw_queue), processed)
        self.update_photo_counter()
        print("created %s" % self.last_photo_bundle)

    def read_photo_counter(self):
        try:
            f = open(self.status_file_name)
            with f:
                self.photo_count = int(f.read())
        except IOError:
            self.photo_count = 0
        except ValueError:
            self.photo_count = 0

    def update_photo_counter(self):
        with open(self.status_file_name, "w") as f:
            f.write(str(self.photo_count))
