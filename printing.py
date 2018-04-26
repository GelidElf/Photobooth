import string
import subprocess
from config import current_config

print_command = 'lpr -P ${printer} ${filename}'
printers = ('Canon_CP910_ipp', 'Canon_CP910_ipp_b')

print_count = 0


def print_image(photo_name):
    global print_count
    print_count += 1
    printer_name = printers[print_count % 2]
    command = string.Template(print_command).safe_substitute(filename=photo_name, printer=printer_name)
    print("executing: '%s'" % command)
    if not current_config.args.test_image:
        subprocess.call(command.split(' '))