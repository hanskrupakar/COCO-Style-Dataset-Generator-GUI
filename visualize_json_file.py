import json
import cv2
import argparse
import os
import numpy as np

if __name__=='__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument('json_file', help="Path to the JSON dataset file to visualize")
    args = ap.parse_args()
    
    cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
    
    with open(args.json_file, 'r') as f:    
        obj = json.loads(f.read())
    
    images, annotations = obj["images"], obj["annotations"]
    classes = obj["classes"]
    
    print ("Dataset contains %d images, %d objects!"%(len(images), len(annotations)))
    for img in images:
        if os.path.exists(img['file_name']):
            anns = [ann for ann in annotations if ann["image_id"]==img["id"]]
            image_cv2 = cv2.imread(img["file_name"])
            ann_img = image_cv2.copy()
            for ann in anns:
                s = [int(x) for x in ann['bbox']]
                seg = np.array(ann['segmentation'][0])
                x, y = seg[range(0, len(seg)-1, 2)], seg[range(1, len(seg), 2)]
                seg2d = [[xi, yi] for xi, yi in zip(x,y)]
                cv2.fillPoly(ann_img, np.array([seg2d], dtype = 'int32'), (0, 255, 0))
                cv2.rectangle(image_cv2, (s[0], s[1]), (s[2], s[3]), (0,0,0), 2)
                cv2.putText(image_cv2, classes[ann['category_id']-1], (s[0]-10, s[1]+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            image_cv2 = cv2.addWeighted(ann_img,0.25,image_cv2,0.75,0)
            cv2.imshow('frame', image_cv2)
            q = cv2.waitKey()
        
            if q == 113: # if q == 'q'
                exit()
