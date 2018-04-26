from flask import Flask
from flask import current_app
from flask import render_template
from flask import send_file
from os import listdir, sep
import printing

app = Flask(__name__)


@app.route("/")
@app.route("/index.html")
def index():
    image_path = current_app.config.generator.raw_path
    photos = listdir(image_path)
    return render_template('index.html', photos=photos)


@app.route("/image/<image_name>")
def image(image_name):
    return send_file(current_app.config.generator.raw_path + sep + image_name, mimetype='image/jpeg')


@app.route("/view/<image_name>")
def view(image_name):
    return render_template('view.html', photo=image_name)


@app.route("/print/<image_name>")
def print_image(image_name):
    image_path = current_app.config.generator.preview_path + sep + image_name
    printing.print_image(image_path)
    return "OK"


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    response.cache_control.public = True
    return response