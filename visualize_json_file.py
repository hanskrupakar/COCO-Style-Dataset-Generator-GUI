import json
import cv2
import argparse
import os
import numpy as np

if __name__=='__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument('json_file', help="Path to the JSON dataset file to visualize")
    ap.add_argument('--save', help='Save a few results to disk to accommodate non-display environments', action='store_true')
    args = ap.parse_args()
    
    '''
    cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
    '''

    with open(args.json_file, 'r') as f:    
        obj = json.loads(f.read())
    
    images, annotations = obj["images"], obj["annotations"]
    classes = obj["classes"]
    
    print ("Dataset contains %d images, %d objects!"%(len(images), len(annotations)))
    
    for idx, img in enumerate(images):
        imgpath = os.path.join(os.path.dirname(args.json_file), img['file_name'])
        if os.path.exists(imgpath):
            anns = [ann for ann in annotations if ann["image_id"]==img["id"]]
            image_cv2 = cv2.imread(imgpath)
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

            if not args.save:
                cv2.imshow('frame', image_cv2)
                q = cv2.waitKey()
            
            else:
                cv2.imwrite('sample%d.jpg'%(idx), image_cv2)
                q = 10    
                if idx > 5:
                    q = 113

            if q == 113: # if q == 'q'
                exit()
