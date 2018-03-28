import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import json
from collections import defaultdict
import random
from matplotlib.path import Path

class Occlusion_Generator_Bbox(object):

    def __init__(self, json_file, bg_path):
    
        self.dataset = json.load(open(json_file))
        self.imgToAnns = defaultdict(list)
        for ann in self.dataset['annotations']:
            self.imgToAnns[ann['image_id']].append(ann)
        
        self.objToAnns = [[] for _ in range(len(self.dataset['classes'])+1)]
        for index in self.imgToAnns:
            for obj in self.imgToAnns[index]:
                self.objToAnns[obj['category_id']].append({'image': obj['image_id'], 'bbox':obj['bbox']})
        
        self.img = Image.open(bg_path).convert("RGBA")
        self.mask_img = Image.new('L', self.img.size, 0)
        
    def cut_bbox(self, rect): # Takes a bounding box of the form [x_min, y_min, x_max, y_max] and splits it in 2 based on a sine wave and returns 2 PIL polygons

        x = np.linspace(rect[0], rect[2], num=50)
        y = (rect[3]+rect[1])/2 + 15*np.sin(x/(rect[3]/np.pi/2))
        
        x1 = np.concatenate((x, np.array([rect[2], rect[0]])))
        y1 = np.concatenate((y, np.array([rect[3], rect[3]])))
        
        x2 = np.concatenate((x, np.array([rect[2], rect[0]])))
        y2 = np.concatenate((y, np.array([rect[1], rect[1]])))
        
        poly1 = [(x,y) for x,y in zip(x1, y1)]
        poly2 = [(x,y) for x,y in zip(x2, y2)]
        
        return random.choice([poly1, poly2])
    
    def add_objects(self, n_objs):
        
        for _ in range(n_objs):

            c1 = random.randint(1, len(self.objToAnns)-1)
            c2 = random.randint(0, len(self.objToAnns[c1])-1)

            obj = Image.open(next(item for item in self.dataset['images'] if item["id"] == self.objToAnns[c1][c2]['image'])['file_name'])
            obj_bbox = self.objToAnns[c1][c2]['bbox']
            obj_bbox = (obj_bbox[2], obj_bbox[3], obj_bbox[0], obj_bbox[1])
            
            obj_mask = Image.new('L', obj.size, 0)      
            random_occ = self.cut_bbox(obj_bbox)   
            ImageDraw.Draw(obj_mask).polygon(random_occ, outline=255, fill=255)
            
            obj = obj.crop(obj_bbox)
            obj_mask = obj_mask.crop(obj_bbox)

            obj = obj.resize(np.array(np.array(obj.size)*1.5, dtype=int))
            obj_mask = obj_mask.resize(np.array(np.array(obj_mask.size)*1.5, dtype=int))

            done_flag = False

            while not done_flag:

                randx = random.randint(0, self.img.size[0]-obj.size[0]-2)
                randy = random.randint(0, self.img.size[1]-obj.size[1]-2)

                temp_mask = self.mask_img.copy()
                temp_mask.paste(Image.new('L', obj_mask.size, 0), (randx, randy))

                if (temp_mask == self.mask_img):
                    self.img.paste(obj, (randx, randy), obj_mask)
                    self.mask_img.paste(obj_mask, (randx, randy))
                    done_flag=True
        self.img.show()

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
    occ = Occlusion_Generator_Bbox('../pascal_dataset.json', 'bg.jpg')
    occ.add_objects(10)
