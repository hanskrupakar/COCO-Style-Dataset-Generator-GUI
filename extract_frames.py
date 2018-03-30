import numpy as np
import cv2
import glob
import argparse
import imutils
import os

if __name__=='__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--videos_dir", required=True, help="Path to the dir of videos") 
    ap.add_argument("-r", "--rotation", required=False, help="Angle of rotation") 
    args = ap.parse_args()

    if not os.path.isdir('frames'):
        os.mkdir('frames')

    for f in glob.glob(os.path.join(args.videos_dir, '*')):

        print (f)
        cap = cv2.VideoCapture(f)
        if not os.path.isdir('frames/'+f.split('/')[-1][:-4]):
            os.mkdir('frames/'+f.split('/')[-1][:-4])
        else:
            continue;

        i = 0
        ret, frame = cap.read()
        frame = imutils.rotate(frame, int(args.rotation))
        while(ret):
            i+=1
            cv2.imwrite('frames/'+f.split('/')[-1][:-4]+'/'+f.split('/')[-1][:-4]+'_%d.jpg'%(i), frame)
            ret, frame = cap.read()
            if ret:
                frame = imutils.rotate(frame, int(args.rotation))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()