#coding: utf8
import xml.etree.cElementTree as ET
import glob
import argparse
import os
import numpy as np
import json
import unicodedata

from PIL import Image
from ..gui.segment import COCO_dataset_generator as cocogen

if __name__=='__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image_dir", required=True, help="Path to the image dir")
    ap.add_argument("-o", "--file_path", required=True, help="Path of output file")
    ap.add_argument("-c", "--class_file", required=True, help="Path of file with output classes")
    ap.add_argument("-t", "--type", required=True, help="Type of the image files")
    args = vars(ap.parse_args())

    with open(args['class_file'], 'r') as f:
        classes = sorted([unicodedata.normalize('NFKD', x).strip() for x in f.readlines()])
        
    images, anns = [], []
	
    img_paths = [x for x in glob.glob(os.path.join(args['image_dir'], '*.'+args['type'])) if os.path.exists(x[:-3]+'txt')]
	
    num_imgs = len(img_paths)
    i=0
    for f in sorted(img_paths):
        
        img = Image.open(f)
        width, height = img.size
        dic = {'file_name': f, 'id': i, 'height': height, 'width': width}
        images.append(dic)

    ann_index = 0
    
    for i, f in enumerate(sorted(glob.glob(os.path.join(os.path.abspath(args['image_dir']), '*.txt')))):
        ptr = 0
        with open(f, 'r', encoding='utf-8-sig') as g:
            s = g.read()
        s = s.split('\n')[2:-1]
        
        width, height = [int(x) for x in s[0].split(' ')]
        s = s[2:]
        print (s)
        while(ptr<len(s)):
            
            cat_id = classes.index(s[ptr].encode('utf-8').decode('utf-8-sig'))+1
            area = float(s[ptr+1])
            poly = [[float(x) for x in s[ptr+2].split(' ')[:-1]]]
            
            print (cat_id, area, poly)

            if len(s)>ptr+3 and s[ptr+3] != '':
                ind = ptr + 3
                while (ind<len(s) and s[ind]!=''):
                    poly.append([float(x) for x in s[ind].split(' ')[:-1]])
                    ind+=1
                ptr = ind-3
            
            x1, x2, y1, y2 = None, None, None, None
            for p in poly:
                points = np.reshape(np.array(p), (int(len(p)/2), 2))
                if x1 is None: 
                    x1, y1 = points.min(0)
                    x2, y2 = points.max(0)
                else:
                    if points.min(0)[0]<x1:
                        x1 = points.min(0)[0]
                    if points.min(0)[1]<y1:
                        y1 = points.min(0)[1]
                    if points.max(0)[0]>x2:
                        x2 = points.max(0)[0]
                    if points.max(0)[1]>y2:
                        y2 = points.max(0)[1]
                        
            bbox = [x2, y2, x1, y1]
            dic2 = {'segmentation': poly, 'area': area, 'iscrowd':0, 'image_id':i, 'bbox':bbox, 'category_id': cat_id, 'id': ann_index}
            ann_index+=1
            ptr+=4
            anns.append(dic2)
          
    data = {'images':images, 'annotations':anns, 'categories':[], 'classes': classes}

    with open(args['file_path']+'.json', 'w') as outfile:
        json.dump(data, outfile)
