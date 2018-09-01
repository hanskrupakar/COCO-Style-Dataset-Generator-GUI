'''
USAGE:
python combine_json_files.py <LIST OF FILES>
'''

import json
import glob
import sys
import numpy as np
import argparse

def cleanup_utf8(array):
    return [x.encode('utf-8').decode('utf-8').strip() for x in array]

if __name__=='__main__':
    
    if len(sys.argv) < 3:
        print ("Not enough input files to combine into a single dataset file")
        exit()
    
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+', help='List of JSON files to combine into single JSON dataset file')
    args = ap.parse_args()
    
    files = args.files
    
    img_counter = 0
    ann_counter = 0
    
    images, annotations, classes = [], [], []
    
    for file_path in files:
        
        with open(file_path, 'r') as f:
            obj = json.load(f)
        
        for img in obj["images"]:
            img["id"] += img_counter
        
        for ann in obj["annotations"]:
            ann["id"] += ann_counter
            ann["image_id"] += img_counter
        
        ann_counter += len(obj["annotations"])
        img_counter += len(obj["images"])
        
        if len(images)==0:
            images = obj['images']
            annotations = obj['annotations']
            classes = cleanup_utf8(obj['classes'])
        else:
            images.extend(obj["images"])
            annotations.extend(obj["annotations"])
            obj['classes'] = cleanup_utf8(obj['classes'])
            if classes != obj["classes"]:
                print ("Dataset mismatch between the JSON files!")
                print ([x==y for x,y in zip(classes, obj['classes'])])
                print (classes, obj['classes'])
                exit()
        
    with open("merged_json.json", "w") as f:
        data = {'images': images, 'annotations':annotations, 'classes': classes, 'categories':[]}
        json.dump(data, f)
