import numpy as np
import cv2
import glob

for f in glob.glob('videos/*'):

    cap = cv2.VideoCapture(f)

    i = 0
    ret, frame = cap.read()
    while(1):
        i+=1
        cv2.imwrite('frames/'+f.split('/')[-1][:-4]+'_%d.jpg'%(i), frame)
        if ((i>100 and 'hans' not in f) or (i>700 and 'hans' in f)):
            break 
        ret, frame = cap.read()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

