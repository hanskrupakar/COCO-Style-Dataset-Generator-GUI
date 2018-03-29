import numpy as np
import cv2
import glob
import sys
import imutils
import os

for f in glob.glob(os.path.join(sys.argv[1], '*')):

    cap = cv2.VideoCapture(f)

    i = 0
    ret, frame = cap.read()
    frame = imutils.rotate(frame, 270)
    while(ret):
        i+=1
        cv2.imwrite('frames/'+f.split('/')[-1][:-4]+'_%d.jpg'%(i), frame)
        ret, frame = cap.read()
        frame = imutils.rotate(frame, 270)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

