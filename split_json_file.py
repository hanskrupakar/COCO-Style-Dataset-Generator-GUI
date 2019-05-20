import json
import argparse

def contains(splits):
# Returns 1D binary map of images to take such that access is O(1)
    MAX, MIN = max([int(x.split('-')[-1]) for x in splits]), min([int(x.split('-')[0]) for x in splits])
    A = [0 for _ in range(MAX-MIN+1)]
    for sp in splits:
        if '-' in sp:
            beg, end = [int(x) for x in sp.split('-')]    
        else:
            beg = end = int(sp)
        for idx in range(beg-MIN, end+1-MIN):
            print (idx)
            A[idx] = 1

    return A, MIN, MAX

if __name__=='__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument('json', help='Path to JSON dataset file')
    ap.add_argument('split', nargs='+', help='Dataset split for splitting')
    ap.add_argument('--out', help='Path to output JSON file', default='cut_dataset.json')
    args = ap.parse_args()
    
    with open(args.json, 'r') as f:
        obj = json.load(f)
    
    A, MIN, MAX = contains(args.split)
    imgs, anns = [], []
    for img in obj['images']:
        if img['id'] >= MIN and img['id'] <= MAX:
            if A[img['id']-MIN]:
                ANN = [ann for ann in obj['annotations'] if ann['image_id']==img['id']]
                anns.extend(ANN)
                imgs.append(img)

    with open(args.out, 'w') as f:
        
        json.dump({'images': imgs, 'annotations': anns, 'classes': obj['classes'], 'categories': []}, f)
            
