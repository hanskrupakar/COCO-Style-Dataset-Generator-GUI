from PIL import Image, ImageChops
import argparse, glob, os, math

def trim(im):
        bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)

if __name__=='__main__':

        ap = argparse.ArgumentParser()
        ap.add_argument("-i", "--images_dir", required=True, help="Path to the dir of images") 
        args = ap.parse_args()

        for f in glob.glob(os.path.join(args.images_dir, '*')):
            im = Image.open(f)
            im = trim(im)
            im.save(f)
