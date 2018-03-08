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

    def __init__(self, strip_width):
        
        self.random_factor = 8
        self.distance = strip_width
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
            
            strips = [Annotation() for _ in range(len(lines[2:]))]
                    
            poly = [(imArray.shape[1], 0), (0, 0)]
            
            for pos, l in enumerate(lines[2:]):
                
                if ptr == 0:

                    x, y = [0, imArray.shape[1]], [l, l+self.distance]
                    y_interp = scipy.interpolate.interp1d(x, y)
                    x_pts, y_pts = [x[0]], [y[0]] 
                    
                    for p in range(0, imArray.shape[1], 5):
                        yt = y_interp(p) + (2*np.random.random_sample()-1)*self.random_factor
                        x_pts.append(p + (2*np.random.random_sample()-1)*self.random_factor)
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
    
    def polys_to_string(self, polys):
        
        ret = ''
        
        for poly in polys:
            for (x, y) in poly:
                ret+='%.2f %.2f '%(x, y)
            ret+='\n'
        return ret
    
    def find_poly_area(self, poly):
        
        x, y = np.zeros(len(poly)), np.zeros(len(poly))
        for i, (xp, yp) in enumerate(poly):
            x[i] = xp
            y[i] = yp
        return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1))) #shoelace algorithm
    
    def generate_samples(self, num, path):
        
        cumulative_mask = None
        text = ''
        
        if not os.path.exists(path):
            os.mkdir(path)
        
        for i in range(num):
        
            newImage = Image.new('RGBA', (self.im_shape[1], self.im_shape[0]), 0)

            text+="occ%d\n%s\n%d %d\n\n"%(i, os.path.join(path, 'occ_%d.jpg'%(i+1)), self.im_shape[0], self.im_shape[1])
            
            for j in range(len(self.all_images[0])):
                
                rand = np.random.randint(len(self.all_images))
                
                # create mask
                maskimg = Image.new('L', (self.im_shape[1], self.im_shape[0]), 0)
                
                ImageDraw.Draw(maskimg).polygon(self.polys[j], outline=1, fill=1)
                mask = np.array(maskimg)
                
                #Image.fromarray(mask*255, 'L').show()
                
                if cumulative_mask is None:
                    cumulative_mask = mask
                else:
                    cumulative_mask += mask 
                
                #Image.fromarray(cumulative_mask*255, 'L').show()
                
                #time.sleep(.5)                
                # assemble new image (uint8: 0-255)
                newImArray = np.empty(self.im_shape[:2]+(4,), dtype='uint8')

                # colors (three first columns, RGB)
                newImArray[:,:,:3] = self.images[rand][:,:,:3]
                
                # transparency (4th column)
                newImArray[:,:,3] = mask*255

                # back to Image from numpy
                
                newIm = Image.fromarray(newImArray, "RGBA")
                
                newImage.paste(newIm, (0, 0), newIm)
                
                for anns, cls in zip(self.all_images[rand][j].objects, self.all_images[rand][j].classes):
                    text += cls+'\n'
                    area = 0
                    for poly in anns:
                        area += self.find_poly_area(poly)
                    text+='%.2f\n'%area
                    text += self.polys_to_string(anns)
                    text +='\n'
                
            background = Image.new("RGB", (newImArray.shape[1], newImArray.shape[0]), (0, 0, 0))
            background.paste(newImage, mask=newImage.split()[3]) # 3 is the alpha channel
                
            background.save(os.path.join(path, 'occ_%d.jpg'%(i+1)))
            with open(os.path.join(path, 'occ_%d.txt'%(i+1)), 'w') as f:
                f.write(text)
            text = ''
            print ('Generated %d/%d Images: %s'%(i+1, num, os.path.join(path, 'occ_%d.jpg'%(i+1))))
                
if __name__=="__main__":
        
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image_dir", required=True, help="Path to the image dir") 
    ap.add_argument("-o", "--output_dir", required=True, help="Path to the output dir") 
    ap.add_argument("-s", "--strip_width", required=True, help="width of strip") 
    ap.add_argument("-n", "--num_images", required=True, help="number of new images to generate") 
    args = vars(ap.parse_args())

    occlusion_gen = Occlusion_Generator(int(args['strip_width']))    
    
    occlusion_gen.generate_samples(int(args['num_images']), args['output_dir'])
