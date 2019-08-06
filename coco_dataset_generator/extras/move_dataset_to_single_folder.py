import argparse
import shutil
import json
import os

if __name__=='__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument('dir', help='Path to folder to put all images in the dataset')
    ap.add_argument('json', help='Path to folder to put all images in the dataset')
    args = ap.parse_args()

    with open(args.json, 'r') as f:
        obj = json.load(f)
    
    try:
        os.makedirs(args.dir)
    except Exception:
        pass

    for idx, img in enumerate(obj['images']):
        
        path = img['file_name']
        newpath = os.path.join(args.dir, '%s.'%(str(idx).zfill(5))+path.split('.')[-1])
        
        shutil.copyfile(path, newpath)
        
        print ("Moving %s to %s"%(path, newpath))

        obj['images'][idx]['file_name'] = newpath
    
    print ("Writing new JSON file!")

    base, direc = os.path.basename(args.dir), os.path.dirname(args.dir)
    
    with open(os.path.join(direc, '%s_dataset.json'%(base)), 'w') as f:
        json.dump(obj, f)
    print ("JSON file written!")
