import os
from matplotlib import pyplot as plt
import sys
import numpy as np
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import glob
import argparse

if __name__=='__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image_dir", required=True, help="Path to the image dir") 
    args = vars(ap.parse_args())
    
    colors = 100*np.random.random(20)
    
    for f in glob.glob(os.path.join(args['image_dir'], '*.jpg')):
    
        image = plt.imread(f)
        fig, ax = plt.subplots()
        
        polys = []
        with open(f[:-3]+'txt', 'r') as f:
            txt = f.read().split('\n')
            
            for index in range(6, len(txt), 4):
                #print (txt[index])
                num = [float(x) for x in txt[index].split(' ')[:-1]]
                num = np.reshape(np.array(num), (int(len(num)/2), 2))
                polys.append(Polygon(num, closed=True))
            ax.imshow(image)
            p = PatchCollection(polys, cmap=matplotlib.cm.jet, linewidths=0, alpha=0.5)
            p.set_array(colors)
            ax.add_collection(p)
            plt.show()
