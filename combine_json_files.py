'''
USAGE:
python combine_json_files.py <LIST OF FILES>
'''
import os
import json
import glob
import sys
import numpy as np
import argparse
import os

def cleanup_utf8(array):
    return [x.encode('ascii', errors='ignore').decode('utf-8').strip() for x in array]

def merge_json(files, outfile='merged_dataset.json', abspath=False):

    img_counter = 0
    ann_counter = 0
    
    images, annotations, classes = [], [], []
    
    for file_path in files:
        
        with open(file_path, 'r') as f:
            obj = json.load(f)
        
        for img in obj["images"]:
            img["id"] += img_counter
<<<<<<< HEAD

            if not abspath:
                img['file_name'] = os.path.join(os.path.abspath(os.path.dirname(file_path)), img['file_name'])
        
=======
            img['file_name'] = os.path.join(
                                os.path.dirname(file_path),
                                img['file_name'])

>>>>>>> 4ce4aa2056b3b0020c831a9a91f753c3a8e0102e
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
            obj['classes'] = cleanup_utf8(obj['classes'])
   
            if classes != obj["classes"]:
                if len(obj['classes']) < len(classes):
                    c1, c2 = obj['classes'], classes
                    new = True
                else:
                    c1, c2 = classes, obj['classes']
                    new = False

                mapping = {}
                for idx, c in enumerate(c1):
                    try:
                        mapping[idx] = c2.index(c)
                    except Exception:
                        c2.append(c)
                        mapping[idx] = len(c2) - 1
                
                if not new:
                    for idx, ann in enumerate(annotations):
                        annotations[idx]['category_id'] = mapping[ann['category_id']]
                    classes = obj['classes']
                else:
                    for idx, ann in enumerate(obj['annotations']):
                        obj['annotations'][idx]['category_id'] = mapping[ann['category_id']]
                    obj['classes'] = classes
            
                print ("CHANGE IN NUMBER OF CLASSES HAS BEEN DETECTED BETWEEN JSON FILES")
                print ("NOW MAPPING OLD CLASSES TO NEW LIST BASED ON TEXTUAL MATCHING")

                for k, v in mapping.items():
                    print (c1[k], "==>", c2[v])
                
                remaining = set(c2) - set(c1)
                for r in remaining:
                    print ("NEW CLASS: ", r)

            images.extend(obj["images"])
            annotations.extend(obj["annotations"])
    
    with open(outfile, "w") as f:
        data = {'images': images, 'annotations':annotations, 'classes': classes, 'categories':[]}
        json.dump(data, f)

if __name__=='__main__':
    
    if len(sys.argv) < 3:
        print ("Not enough input files to combine into a single dataset file")
        exit()
    
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+', help='List of JSON files to combine into single JSON dataset file')
    ap.add_argument('--absolute', nargs='+', help='Flag to use absolute paths in JSON file')
    args = ap.parse_args()
    
    merge_json(args.files, 'merged_json.json', args.absolute)
    
    
