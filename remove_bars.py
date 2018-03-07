from PIL import Image, ImageChops
import sys, glob, os

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

if __name__=='__main__':

    for f in glob.glob(os.path.join(sys.argv[1], '*.jpg')):

        im = Image.open(f)
        im = trim(im).resize((1920, 1080), Image.ANTIALIAS)
        im.save(f)


