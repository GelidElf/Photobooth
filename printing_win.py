import string
import subprocess
import win32print, win32ui
from PIL import Image, ImageWin

print_command = 'rundll32 C:\Windows\System32\shimgvw.dll ImageView_PrintTo "${filename}" "${printer}"'
printers = ['sinfonia']

def print_image(self):
    photo_name = self.generator.last_photo_bundle.processed
    if current_config.args.win_env:
        photo_name = photo_name.replace(r'\\', r'\\\\')
        print("win_filename: '%s'" % photo_name)
    self.print_count += 1
    if len(printers) > 1:
        printer_name = printers[self.print_count % 2]
    else:
        printer_name = printers[0]
    #command = string.Template(print_command).safe_substitute(filename=photo_name, printer=printer_name)
    #command = command.replace(r'\\', r'\\\\')
    #print("executing: '%s'" % command)
    if not self.test_image:
        #win32api.ShellExecute (0, "print", photo_name, '/d: "%s"' % printer_name, ".", 0)
        #subprocess.call(command.split(' '))
        dc = win32ui.CreateDC()
        dc.CreatePrinterDC(printer_name)

        photo = Image.open(photo_name)
        dc.StartDoc(photo_name)
        dc.StartPage()
        dib = ImageWin.Dib(photo)
        x1, y1, x2, y2 = 0, 0, 1280, 1920
        dib.draw(dc.GetHandleOutput(), (x1, y1, x2, y2))
        dc.EndPage()
        dc.EndDoc()
        dc.DeleteDC()