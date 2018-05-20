import numpy as np
import cv2
import glob
import argparse
import imutils
import os

if __name__=='__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--videos_dir", required=True, help="Path to the dir of videos") 
    ap.add_argument("-o", "--frames_dir", required=True, help="Path to the output dir")
    ap.add_argument("-r", "--rotation", required=False, help="Angle of rotation") 
    args = ap.parse_args()

    if not os.path.isdir(args.frames_dir):
        os.mkdir(args.frames_dir)

    for f in glob.glob(os.path.join(args.videos_dir, '*')):

        print (f)
        cap = cv2.VideoCapture(f)
        if not os.path.isdir(os.path.join(args.frames_dir, f.split('/')[-1][:-4])):
            os.mkdir(os.path.join(args.frames_dir, f.split('/')[-1][:-4]))
        
        i = 0
        ret, frame = cap.read()
        while(ret):

            i+=1
            
            if args.rotation is not None:
                frame = imutils.rotate_bound(frame, int(args.rotation))
            
            if os.path.exists(os.path.join(*[args.frames_dir, f.split('/')[-1][:-4], f.split('/')[-1][:-4]+'_%d.jpg'%(i)])):
                continue
            else:
                cv2.imwrite(os.path.join(*[args.frames_dir, f.split('/')[-1][:-4], f.split('/')[-1][:-4]+'_%d.jpg'%(i)]), frame)
            
            ret, frame = cap.read()

        cap.release()
