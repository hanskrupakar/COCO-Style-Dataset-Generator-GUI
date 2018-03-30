from PIL import Image, ImageChops
import argparse, glob, os, math

def trim(im):
        bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)

def rotatedRectWithMaxArea(w, h, angle):

    if w <= 0 or h <= 0:
        return 0,0

    max_side, min_side = (w,h) if w >= h else (h,w)
    sin_a, cos_a = abs(math.sin(angle)), abs(math.cos(angle))
    
    if min_side <= 2.*sin_a*cos_a*side_long or abs(sin_a-cos_a) < 1e-10:
        x = 0.5*min_side
        wr,hr = (x/sin_a,x/cos_a) if w >= h else (x/cos_a,x/sin_a)
    else:
        cos_2a = cos_a*cos_a - sin_a*sin_a
        wr,hr = (w*cos_a - h*sin_a)/cos_2a, (h*cos_a - w*sin_a)/cos_2a

    return wr,hr

if __name__=='__main__':

        ap = argparse.ArgumentParser()
        ap.add_argument("-i", "--images_dir", required=True, help="Path to the dir of images") 
        args = ap.parse_args()

        for f in glob.glob(os.path.join(args.images_dir, '*')):
                im = Image.open(f)
                im = trim(im)
                #print (rotatedRectWithMaxArea(1920, 1080, 90))
                im.save(f)