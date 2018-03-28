import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import json
from collections import defaultdict
import random
from matplotlib.path import Path
import argparse
import glob
import os
import time
from skimage.measure import find_contours

class Occlusion_Generator_Bbox(object):

    def __init__(self, json_file, bg_dir, max_objs):
    
        self.dataset = json.load(open(json_file))
        self.max_objs = max_objs

        self.imgToAnns = defaultdict(list)
        for ann in self.dataset['annotations']:
            self.imgToAnns[ann['image_id']].append(ann)
        
        self.objToAnns = [[] for _ in range(len(self.dataset['classes'])+1)]
        for index in self.imgToAnns:
            for obj in self.imgToAnns[index]:
                self.objToAnns[obj['category_id']].append({'image': obj['image_id'], 'bbox':obj['bbox']})
        
        self.bg_dir = bg_dir

        self.set_random_background()
    
    def set_random_background(self):

        bg_path = random.choice(glob.glob(os.path.join(self.bg_dir, '*')))
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
    
    def add_objects(self): #Adds enlarged versions of n_objs (RANDOM) objects to self.img at random locations without overlap
        
        n_objs = random.randint(5, self.max_objs)
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

            obj = obj.resize(np.array(np.array(obj.size)*1.35, dtype=int))
            obj_mask = obj_mask.resize(np.array(np.array(obj_mask.size)*1.35, dtype=int))

            done_flag, timeout = False, False
            clk = time.time()

            while not done_flag:

                if time.time()-clk > 1:
                    timeout = True

                randx = random.randint(0, self.img.size[0]-obj.size[0]-2)
                randy = random.randint(0, self.img.size[1]-obj.size[1]-2)

                temp_mask = self.mask_img.copy()
                temp_mask.paste(Image.new('L', obj_mask.size, 0), (randx, randy))

                if (temp_mask == self.mask_img):
                    
                    self.img.paste(obj, (randx, randy), obj_mask)
                    self.mask_img.paste(obj_mask, (randx, randy))

                    obj_ann = Image.new('L', self.mask_img.size, 0)
                    obj_ann.paste(obj_mask, (randx, randy))

                    padded_mask = np.zeros((obj_ann.size[0] + 2, obj_ann.size[1] + 2), dtype=np.uint8)
                    padded_mask[1:-1, 1:-1] = np.array(obj_ann)
                    contours = find_contours(padded_mask, 0.5)
                    for verts in contours:
                        verts = np.fliplr(verts) - 1
                        t_im = Image.new('L', self.mask_img.size, 0)
                        ImageDraw.Draw(t_im).polygon([(x,y) for [x, y] in verts], outline=255, fill=255)
                    
                        
                    done_flag=True
        
                if not done_flag and timeout:

                    print ('Object Timeout')
                    timeout = False
                    c2 = random.randint(0, len(self.objToAnns[c1])-1)

                    obj = Image.open(next(item for item in self.dataset['images'] if item["id"] == self.objToAnns[c1][c2]['image'])['file_name'])
                    obj_bbox = self.objToAnns[c1][c2]['bbox']
                    obj_bbox = (obj_bbox[2], obj_bbox[3], obj_bbox[0], obj_bbox[1])
                    
                    obj_mask = Image.new('L', obj.size, 0)      
                    random_occ = self.cut_bbox(obj_bbox)   
                    ImageDraw.Draw(obj_mask).polygon(random_occ, outline=255, fill=255)
                    
                    obj = obj.crop(obj_bbox)
                    obj_mask = obj_mask.crop(obj_bbox)

                    obj = obj.resize(np.array(np.array(obj.size)*1.35, dtype=int))
                    obj_mask = obj_mask.resize(np.array(np.array(obj_mask.size)*1.35, dtype=int))


        self.img.show()

    #def create_images(self, num_imgs):



if __name__=='__main__':

    parser = argparse.ArgumentParser(
        description='Create occluded dataset.')
    parser.add_argument('--json_file', required=True,
                        metavar="/path/to/json_file/",
                        help='Path to JSON file', default='../pascal_dataset.json')
    parser.add_argument('--bg_dir', required=True,
                        metavar="/path/to/possible/background/images",
                        help="Path to Background Images", default='background/')
    parser.add_argument('--max_objs', required=True,
                        help="Maximum number of objects in an image (min=5)", default='10')
    parser.add_argument('--num_imgs', required=True,
                        help="Total number of images in the synthetic dataset", default='50')
    args = parser.parse_args()

    occ = Occlusion_Generator_Bbox(args.json_file, args.bg_dir, int(args.max_objs))
    occ.add_objects()
