import argparse
import json

if __name__=='__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument('json', help='Path to original multi-class JSON file')
    args = ap.parse_args()

    with open(args.json, 'r') as f:     
        obj = json.load(f)

    obj['classes'] = ['object']

    for idx in range(len(obj['annotations'])):        
        obj['annotations'][idx]['category_id'] = 1

    with open('.'.join(args.json.split('.')[:-1])+'_binary.json', 'w') as f:
        json.dump(obj, f)

