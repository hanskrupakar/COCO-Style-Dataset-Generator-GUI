import json
import cv2
import argparse

if __name__=='__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument('--json_file', required=True, help="Path to the JSON dataset file to visualize")
    args = ap.parse_args()
    
    cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
    
    with open(args.json_file, 'r') as f:    
        obj = json.loads(f.read())
    
    images, annotations = obj["images"], obj["annotations"]
    classes = obj["classes"]
    
    for img in images:
        anns = [ann for ann in annotations if ann["image_id"]==img["id"]]
        image_cv2 = cv2.imread(img["file_name"])
        for ann in anns:
            s = [int(x) for x in ann['bbox']]
            cv2.rectangle(image_cv2, (s[0], s[1]), (s[2], s[3]), (0,0,0), 2)
            cv2.putText(image_cv2, classes[ann['category_id']-1], (s[0]-10, s[1]+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.imshow('frame', image_cv2)
        cv2.waitKey()
