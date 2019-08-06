import json
import argparse
import numpy as np
import cv2
import os

class DatasetStatistics:
    
    def __init__(self, json_file):
        
        with open(json_file, 'r') as f:
            self.json_obj = json.load(f)
        
        class_list = sorted(self.json_obj['classes'])
        
        self.class_counts = np.zeros(len(class_list), dtype=int)
        for ann in self.json_obj['annotations']:
            self.class_counts[ann['category_id']-1]+=1
        
    def print_occurrences(self):
        
        class_counts, class_list = zip(*sorted(zip(self.class_counts, sorted(self.json_obj['classes']))))
        print ("\n".join([x+": "+str(y)+" occurrences" for x,y in zip(class_list, class_counts)]))
    
    def compute_mean_rgb(self):
        
        cnt, img_sum = 0, np.array([0,0,0], dtype='float')
        
        for img in self.json_obj['images']:
            if os.path.exists(img['file_name']):
                print ("Processing ", img['file_name'])
                
                img = cv2.cvtColor(cv2.imread(img['file_name']), cv2.COLOR_BGR2RGB)
                cnt+= np.prod(img.shape[:2])
                img_sum += np.sum(np.sum(img, axis=0), axis=0) 
        
        img_sum /= cnt
        
        print ("Mean RGB: ", img_sum)   
        
if __name__=='__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument('-j', '--json_file', required=True, help='Path to dataset JSON file created')
    args = ap.parse_args()
    
    stat = DatasetStatistics(args.json_file)
    stat.print_occurrences()
    stat.compute_mean_rgb()
