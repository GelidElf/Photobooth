import os
from datetime import datetime

from flask import Flask
from flask import current_app
from flask import render_template
from flask import send_file

try:
    import printing_win as print_helper
except ImportError:
    import printing as print_helper

app = Flask(__name__)


@app.route("/")
@app.route("/index.html")
def index():
    image_path = current_app.config.generator.raw_path
    profile = current_app.config.profile
    photos_names = reversed(os.listdir(image_path))
    photos = map(lambda p: (p, image_time(image_path, p)), photos_names)
    return render_template('index.html', photos=photos, profile=profile)


def image_time(image_path, p):
    return datetime.fromtimestamp(os.path.getmtime(os.path.join(image_path, p))).strftime("%x %X")


@app.route("/image/<image_name>")
def image(image_name):
    small_image = os.path.join(current_app.config.generator.web_path, image_name)
    if os.path.exists(small_image):
        return send_file(small_image, mimetype='image/jpeg')
    else:
        standard_image = os.path.join(current_app.config.generator.raw_path, image_name)
        return send_file(standard_image, mimetype='image/jpeg')


@app.route("/view/<image_name>")
def view(image_name):
    return render_template('view.html', photo=image_name)


@app.route("/print/<image_name>")
def print_image(image_name):
    image_path = os.path.join(current_app.config.generator.preview_path, image_name)
    print_helper.print_image(image_path)
    return "Sending %s to be printed" % image_name


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    response.cache_control.public = True
    return response
