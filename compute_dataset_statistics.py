import json
import argparse
import numpy as np

if __name__=='__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument('-j', '--json_file', required=True, help='Path to dataset JSON file created')
    args = ap.parse_args()
    
    with open(args.json_file, 'r') as f:
        obj = json.loads(f.read())
    
    class_list = sorted(obj['classes'])
    
    class_counts = np.zeros(len(class_list), dtype=int)
    
    for ann in obj['annotations']:
        
        class_counts[ann['category_id']-1]+=1
    
    class_counts, class_list = zip(*sorted(zip(class_counts, class_list)))
    print ("\n".join([x+": "+str(y)+" occurrences" for x,y in zip(class_list, class_counts)]))
    
        

