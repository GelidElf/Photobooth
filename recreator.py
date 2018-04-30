import argparse
from photo.photo_bundle import PhotoBundle

import os
from os import listdir
from os.path import isabs,isdir,isfile, join
from config import current_config
from processor_pillow import Processor

parser = argparse.ArgumentParser(description='Photobooth Process Recreator.')
parser.add_argument('-o', '--origin')
parser.add_argument('--output_path', default=current_config.ROOT_DIR)
parser.add_argument('--process', choices=('single', 'two', 'dual', 'double', 'four', 'four_album'))
parser.add_argument('--banner')

args = parser.parse_args()


def absolute_path (f):
    return os.path.abspath(join(args.origin, f))


current_config.update_globals((100,100), args)

origin_path = args.origin
if not isabs(origin_path):
    origin_path = join(os.curdir,origin_path)
if not os.path.isdir(args.origin):
    print "--origin parameter is not a directory"

output_path = args.output_path
if not isabs(output_path):
    output_path = join(os.curdir,output_path)
if not os.path.exists(output_path):
    os.makedirs(output_path)
else:
    if not isdir(output_path):
        print "Output '%s'is not directory" % output_path
        exit(-1)

images = [f for f in listdir(origin_path) if isfile(join(origin_path, f)) and not f.startswith('.')]

if len(images) % 2 == 1:
    images.append(str(images[0]))

if args.process in ('two','double'):
    zipped = zip(images[0::2], images[1::2])
else:
    zipped = [[f] for f in images]

for f in zipped:
    processor = Processor(os.path.abspath(args.banner), current_config.args.process)
    print "procesing %s" % str(f)
    raw = map(absolute_path,f)
    print raw
    processed =  os.path.abspath(join(args.output_path,f[0]))
    pb = PhotoBundle(raw,processed)
    processor.process_image(pb, True)
    print "completed %s" % f[0]
print "DONE!"

