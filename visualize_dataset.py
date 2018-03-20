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
    ap.add_argument("-s", "--save", help="save instance of annotated image", action='store_true') 
    args = vars(ap.parse_args())
    
    colors = 100*np.random.random(20)
    
    for f in glob.glob(os.path.join(args['image_dir'], '*.jpg')):
    
        image = plt.imread(f)
        fig, ax = plt.subplots()
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        polys = []
        with open(f[:-3]+'txt', 'r') as f:
            txt = f.read().split('\n')
            
            index = 6
            #for index in range(6, len(txt), 4):
            while (index < len(txt)):
                #print (txt[index])
                num = [float(x) for x in txt[index].split(' ')[:-1]]
                num = np.reshape(np.array(num), (int(len(num)/2), 2))
                polys.append(Polygon(num, closed=True))
                
                while index+1<len(txt) and txt[index+1]!='':
                    index+=1
                    num = [float(x) for x in txt[index].split(' ')[:-1]]
                    num = np.reshape(np.array(num), (int(len(num)/2), 2))
                    polys.append(Polygon(num, closed=True))
                index+=4
                
            ax.imshow(image)
            p = PatchCollection(polys, cmap=matplotlib.cm.jet, linewidths=0, alpha=0.5)
            p.set_array(colors)
            ax.add_collection(p)

            if args['save']:
                plt.savefig('saved_fig.jpg', bbox_inches='tight')
            else:
                plt.show()
