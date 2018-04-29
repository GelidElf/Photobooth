from flask import Flask
from flask import current_app
from flask import render_template
from flask import send_file
import os
from os import listdir, sep
try:
    import printing_win as print_helper
except ImportError:
    import printing as print_helper
'''
if os.name == 'nt': # sys.platform == 'win32':
    import printing_win as print_helper
else:
    import printing as print_helper
'''

app = Flask(__name__)


@app.route("/")
@app.route("/index.html")
def index():
    image_path = current_app.config.generator.raw_path
    profile = current_app.config.profile
    photos = listdir(image_path)
    return render_template('index.html', photos=photos, profile=profile)


@app.route("/image/<image_name>")
def image(image_name):
    return send_file(current_app.config.generator.raw_path + sep + image_name, mimetype='image/jpeg')


@app.route("/view/<image_name>")
def view(image_name):
    return render_template('view.html', photo=image_name)


@app.route("/print/<image_name>")
def print_image(image_name):
    image_path = current_app.config.generator.preview_path + sep + image_name
    print_helper.print_image(image_path)
    return "Sending %s to be printed" % image_name


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    response.cache_control.public = True
    return response