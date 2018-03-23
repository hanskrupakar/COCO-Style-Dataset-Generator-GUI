import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import json
from collections import defaultdict
import random
from matplotlib.path import Path

class Occlusion_Generator_Bbox(object):

    def __init__(self, json_file):
        
        self.dataset = json.load(open(json_file))
        
        imgToAnns = defaultdict(list)
        for ann in self.dataset['annotations']:
            imgToAnns[ann['image_id']].append(ann)
        
        objToAnns = [[] for _ in range(len(self.dataset['classes'])+1)]
        for index in imgToAnns:
            for obj in imgToAnns[index]:
                objToAnns[obj['category_id']].append({'image': obj['image_id'], 'bbox':obj['bbox']})
        

    def cut_bbox(self, rect): # Takes a bounding box of the form [x_min, y_min, x_max, y_max] and splits it in 2 based on a sine wave and returns 2 PIL polygons

        x = np.linspace(rect[0], rect[2], num=50)
        y = (rect[3]+rect[1])/2 + 15*np.sin(x/(500/np.pi/2))
        
        x1 = np.concatenate((x, np.array([rect[2], rect[0]])))
        y1 = np.concatenate((y, np.array([rect[3], rect[3]])))
        
        x2 = np.concatenate((x, np.array([rect[2], rect[0]])))
        y2 = np.concatenate((y, np.array([rect[1], rect[1]])))
        
        poly1 = [(x,y) for x,y in zip(x1, y1)]
        poly2 = [(x,y) for x,y in zip(x2, y2)]
        
        return random.choice([poly1, poly2])
    
    def create_canvas(self, bg_path):
        
        im = Image.open(bg_path).convert("RGBA")
        
        # Create mask
        img = Image.new('L', (width, height), 0)
        ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
        mask = numpy.array(img)
    
    '''
    def generate_images(num, path):
            
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
    '''

if __name__=='__main__':
    occ = Occlusion_Generator_Bbox()
    print (occ.cut_bbox([50, 100, 500, 500]))
