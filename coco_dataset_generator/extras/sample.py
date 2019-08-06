import glob, os
import shutil
import argparse

if __name__=='__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--frames_dir", required=True, help="Path to the dir of videos") 
    ap.add_argument("-n", "--frame_gap", required=True, help="Number of frames per sample") 
    args = ap.parse_args()
    
    for folder in glob.glob(os.path.join(args.frames_dir, '*')):
        for i, f in enumerate(sorted(glob.glob(os.path.join(folder, '*')))):
            if(i%int(args.frame_gap)!=0):
                os.remove(f)
