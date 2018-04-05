import os
from matplotlib import pyplot as plt
import sys
import numpy as np
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from PIL import Image
import glob
import argparse

def return_info(filename):
    
    polys, objects = [], []
    with open(filename, 'r') as f:
        txt = f.read().split('\n')
        
        index = 6
        #for index in range(6, len(txt), 4):
        while (index < len(txt)):
            #print (txt[index])
            numbers = txt[index].split(' ') if txt[index].split(' ')[-1]!='' else txt[index].split(' ')[:-1]
            num = [float(x) for x in numbers]
            
            num = np.reshape(np.array(num), (int(len(num)/2), 2))
            polys.append(num)
            objects.append(txt[index-2])
            
            while index+1<len(txt) and txt[index+1]!='':
                index+=1
                numbers = txt[index].split(' ') if txt[index].split(' ')[-1]!='' else txt[index].split(' ')[:-1]
                
                num = [float(x) for x in numbers]
                num = np.reshape(np.array(num), (int(len(num)/2), 2))
                polys.append(num)
            index+=4
    return polys, objects

if __name__=='__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image_dir", required=True, help="Path to the image dir") 
    ap.add_argument("-s", "--save", help="save instance of annotated image", action='store_true') 
    args = vars(ap.parse_args())
    
    images = [x for x in glob.glob(os.path.join(args['image_dir'], '*.jpg')) if os.path.exists(x[:-3]+'txt')]
    
    for f in images:
    
        fig, ax = plt.subplots()
        colors = 100*np.random.random(20)
        image = plt.imread(f)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        
        polys, objects = return_info(f[:-3]+'txt')        
        polys = [Polygon(num, closed=True) for num in polys]
    
        ax.imshow(image)
        p = PatchCollection(polys, cmap=matplotlib.cm.jet, linewidths=0, alpha=0.5)
        p.set_array(colors)
        ax.add_collection(p)

        if args['save']:
            plt.savefig('saved_fig.jpg', bbox_inches='tight')
        else:
            plt.show()
