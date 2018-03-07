import numpy as np
import glob
import os
import argparse
import scipy.interpolate
import time
from shapely.geometry import Polygon
from skimage.measure import find_contours

from PIL import Image, ImageDraw

class Occlusion_Generator(object):

    def __init__(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-i", "--image_dir", required=True, help="Path to the image dir") 
        args = vars(ap.parse_args())

        self.factor = 8
        self.distance = 100
        class Annotation(object):
            
            def __init__(self):
                
                self.objects = []
                self.classes = []
        
        self.all_images = []
        
        self.images = []
        
        self.polys = []
        
        self.im_shape = np.asarray(Image.open(glob.glob(os.path.join(args["image_dir"], "*.jpg"))[0])).shape
        
        for ptr, f in enumerate(glob.glob(os.path.join(args["image_dir"], "*.jpg"))):

            print ("Processing Image %d/%d"%(ptr+1, len(glob.glob(os.path.join(args["image_dir"], "*.jpg")))))

            im = Image.open(f).convert('RGBA')
            im.load()
            
            self.images.append(np.asarray(Image.open(f)))
            
            # convert to numpy (for convenience)
            imArray = np.asarray(im)
            
            lines = [x for x in range(50, imArray.shape[0], 100)]
            
            image_contents = Annotation()
                    
            with open(f[:-3]+'txt', 'r') as f:
                txt = f.read().split('\n')
                
                for index in range(6, len(txt), 4):
                    
                    num = [float(x) for x in txt[index].split(' ')[:-1]]
                    num = [(num[i], num[i+1]) for i in range(0, len(num), 2)]
                    image_contents.objects.append([num])
                    image_contents.classes.append(txt[index-2])
            
            strips = [Annotation() for _ in range(len(lines[2:-1]))]
                    
            poly = [(imArray.shape[1], 0), (0, 0)]
            
            for pos, l in enumerate(lines[2:-1]):
                
                if ptr == 0:

                    x, y = [0, imArray.shape[1]], [l, l+self.distance]
                    y_interp = scipy.interpolate.interp1d(x, y)
                    x_pts, y_pts = [x[0]], [y[0]] 
                    
                    for p in range(0, imArray.shape[1], 5):
                        yt = y_interp(p) + (2*np.random.random_sample()-1)*self.factor
                        x_pts.append(p + (2*np.random.random_sample()-1)*self.factor)
                        y_pts.append(yt)
                    x_pts.append(x[1])
                    y_pts.append(y[1])
                    
                    pts = [(x, y) for x, y in zip(x_pts, y_pts)]
                    poly.extend(pts)
                    
                    self.polys.append(poly)
                
                else:
                    
                    poly = self.polys[pos]
                
                #ImageDraw.Draw(im).polygon(poly, fill="white", outline=None)
                
                #ImageDraw.Draw(im).line(pts, fill=128)
                
                #im.show()
                #time.sleep(.1)
                
                # create mask
                
                maskimg = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
                ImageDraw.Draw(maskimg).polygon(poly, outline=1, fill=1)
                mask = np.array(maskimg)
                #maskimg.show()
                
                for i in range(len(image_contents.classes)):
                    
                    obj_img = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
                    ImageDraw.Draw(obj_img).polygon(image_contents.objects[i][0], outline=1, fill=1)
                    obj = np.array(obj_img)
                    logical_and = mask * obj
                    
                    if (np.sum(logical_and)>150):
                        
                        # Mask Polygon
                        # Pad to ensure proper polygons for masks that touch image edges.
                        padded_mask = np.zeros(
                            (logical_and.shape[0] + 2, logical_and.shape[1] + 2), dtype=np.uint8)
                        padded_mask[1:-1, 1:-1] = logical_and
                        contours = find_contours(padded_mask, 0.5)
                        
                        strips[pos].objects.append([np.fliplr(verts) - 1 for verts in contours])
                        strips[pos].classes.append(image_contents.classes[i])
            
                if ptr == 0:
                    poly = list(map(tuple, np.flip(np.array(pts), 0)))
            self.all_images.append(strips)
    
    def generate_samples(self, num):
        
        for i in range(num):
            for j in range(len(self.all_images[0])):
                
                rand = np.random.randint(len(self.all_images))
                
                # create mask
                maskimg = Image.new('L', (self.im_shape[1], self.im_shape[0]), 0)
                ImageDraw.Draw(maskimg).polygon(self.polys[j], outline=1, fill=1)
                mask = np.array(maskimg)
                
                # assemble new image (uint8: 0-255)
                newImArray = np.empty(self.im_shape[:2]+(4,), dtype='uint8')

                # colors (three first columns, RGB)
                newImArray[:,:,:3] = self.images[rand][:,:,:3]
                
                # transparency (4th column)
                newImArray[:,:,3] = mask*255

                # back to Image from numpy
                newIm = Image.fromarray(newImArray, "RGBA")
                
                background = Image.new("RGB", self.images[rand].shape[:2], (255, 255, 255))
                background.paste(Image.fromarray(self.images[rand], 'RGB'), mask=newIm.split()[3]) # 3 is the alpha channel
                
                background.show()


if __name__=="__main__":

    occlusion_gen = Occlusion_Generator()    
    
    occlusion_gen.generate_samples(1)
