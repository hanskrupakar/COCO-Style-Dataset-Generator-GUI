import numpy as np
import glob
import os
import argparse
import scipy.interpolate
import time
from shapely.geometry import Polygon

from PIL import Image, ImageDraw

if __name__=="__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image_dir", required=True, help="Path to the image dir") 
    args = vars(ap.parse_args())

    factor = 8
    distance = 100

    for f in glob.glob(os.path.join(args["image_dir"], "*.jpg")):

        im = Image.open(f).convert('RGBA')
        im.load()

        # convert to numpy (for convenience)
        imArray = np.asarray(im)
        
        lines = [x for x in range(50, imArray.shape[0], 100)]
        
        poly = [(imArray.shape[1], 0), (0, 0)]
        polys = []
        
        for l in lines[2:-1]:
            x, y = [0, imArray.shape[1]], [l, l+distance]
            y_interp = scipy.interpolate.interp1d(x, y)
            x_pts, y_pts = [x[0]], [y[0]] 
            
            for p in range(0, imArray.shape[1], 5):
                yt = y_interp(p) + (2*np.random.random_sample()-1)*factor
                x_pts.append(p + (2*np.random.random_sample()-1)*factor)
                y_pts.append(yt)
            x_pts.append(x[1])
            y_pts.append(y[1])
            
            pts = [(x, y) for x, y in zip(x_pts, y_pts)]
            poly.extend(pts)
            
            polys.append(poly)
            
            #ImageDraw.Draw(im).polygon(poly, fill="white", outline=None)
            
            #ImageDraw.Draw(im).line(pts, fill=128)
            #im.show()
            time.sleep(1)
            
            # create mask
            
            maskimg = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
            ImageDraw.Draw(maskimg).polygon(poly, outline=1, fill=1)
            mask = np.array(maskimg)
            #maskimg.show()
            
            # assemble new image (uint8: 0-255)
            newImArray = np.empty(imArray.shape, dtype='uint8')

            # colors (three first columns, RGB)
            newImArray[:,:,:3] = imArray[:,:,:3]
            
            #print (poly)
            
            # transparency (4th column)
            newImArray[:,:,3] = mask*255

            # back to Image from numpy
            newIm = Image.fromarray(newImArray, "RGBA")
            
            background = Image.new("RGB", im.size, (255, 255, 255))
            background.paste(im, mask=newIm.split()[3]) # 3 is the alpha channel
            
            background.show()
            #newIm = Image.composite(newImArray, Image.new('RGBA', (imArray.shape[1], imArray.shape[0]), 'white'), mask)
            #newIm.save('out.png')
            
            poly = list(map(tuple, np.flip(np.array(pts), 0)))

            '''
                # Mask Polygon
                # Pad to ensure proper polygons for masks that touch image edges.
                padded_mask = np.zeros(
                    (mask.shape[0] + 2, mask.shape[1] + 2), dtype=np.uint8)
                padded_mask[1:-1, 1:-1] = mask
                contours = find_contours(padded_mask, 0.5)
                for verts in contours:
                    # Subtract the padding and flip (y, x) to (x, y)
                    
                    verts = np.fliplr(verts) - 1
                    pat = PatchCollection([Polygon(verts, closed=True)], facecolor='green', linewidths=0, alpha=0.6)    
            '''
