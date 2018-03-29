import os
import argparse
import glob
import xml.etree.ElementTree as ET
import json

from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.2f')

import cv2

if __name__=='__main__':
	

    ap = argparse.ArgumentParser(description='Convert PASCAL VOC format dataset to COCO style dataset')
    ap.add_argument("-d", "--pascal_dir", required=True, help="Path to the PASCAL VOC style dataset")
    ap.add_argument("-c", "--class_file", required=True, help="Path to the classes in the dataset")
    ap.add_argument("-n", "--file_name", required=True, help="Name of output JSON file")
    args = vars(ap.parse_args())

    with open(args['class_file'], 'r') as f:
	    classes = [x.strip() for x in f.readlines()]   

    images, anns = [], []
    ann_index = 0
    
    for i, f in enumerate(glob.glob(os.path.join(args['pascal_dir'], 'JPEGImages/*.png'))):
        annot = os.path.join(args['pascal_dir'], 'Annotations', f.split('/')[-1][:-3]+'xml')
        tree = ET.parse(annot)
        root = tree.getroot()         
    
        img = cv2.imread(f)
        height, width, _ = img.shape
        dic = {'file_name': os.path.abspath(f), 'id': i, 'height': height, 'width': width}
        images.append(dic)

        for obj in root.findall('object'):
       
            cls_id = classes.index(obj.find('name').text)+1
            bx = [int(obj.find('bndbox').find('xmax').text), int(obj.find('bndbox').find('ymax').text), int(obj.find('bndbox').find('xmin').text), int(obj.find('bndbox').find('ymin').text)]
            pts = [bx[0], bx[1], bx[2], bx[1], bx[2], bx[3], bx[0], bx[3], bx[0], bx[1]] # Create mask as the bounding box itself
            area = (bx[0]-bx[2])*(bx[1]-bx[3])
            dic2 = {'segmentation': [pts], 'area': area, 'iscrowd':0, 'image_id':i, 'bbox':bx, 'category_id': cls_id, 'id': ann_index}
            ann_index+=1
            anns.append(dic2)

    data = {'images':images, 'annotations':anns, 'categories':[], 'classes':classes}

    with open(args['file_name']+'.json', 'w') as outfile:
        json.dump(data, outfile)
