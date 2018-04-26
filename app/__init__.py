''' a
# This class will handles any incoming request from
# the browser
class myHandler(BaseHTTPRequestHandler):

    # Handler for the GET requests
    def do_GET(self):
        global static_path, image_path

        split_path = self.path.split('?')
        self.path = split_path[0]
        if len(split_path) == 2:
            domain = split_path[1]
        else:
            domain = ''

        if self.path == "/":
            self.path = "/index.html"

        try:
            # Check the file extension required and
            # set the right mime type

            send_reply = False
            if self.path.endswith("index.html"):
                self.path = static_path + self.path
                mimetype = 'text/html'
                send_reply = True
                html = """

                """
                files = listdir(image_path)
                images_html = ""
                for image in files:
                    images_html = images_html + (html % (image, image, image))

                f = open(self.path, 'rb')
                content = f.read() % (images_html)
            if self.path.endswith("view.html"):
                self.path = static_path + self.path
                mimetype = 'text/html'
                send_reply = True
            if self.path.endswith(".jpg"):
                self.path = image_path + self.path
                mimetype = 'image/jpeg'
                send_reply = True
            if self.path.endswith(".png"):
                mimetype = 'image/png'
                send_reply = True
            if self.path.endswith(".gif"):
                mimetype = 'image/gif'
                send_reply = True
            if self.path.endswith(".js"):
                mimetype = 'application/javascript'
                send_reply = True
            if self.path.endswith(".css"):
                mimetype = 'text/css'
                send_reply = True

            if send_reply == True:
                # Open the templates file requested and send it
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.send_header('Cache-Control', 'public,max-age=84600')
                self.end_headers()
                self.wfile.write(content)
                f.close()
            return


        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)
'''