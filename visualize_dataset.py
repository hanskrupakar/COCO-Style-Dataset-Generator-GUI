import os
from matplotlib import pyplot as plt
import sys
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


image = plt.imread(sys.argv[1])
fig, ax = plt.subplots()

with open(sys.argv[1][:-3]+'txt', 'r') as f:
    txt = f.read().split('\n')
    num = [float(x) for x in txt[6].split(' ')[:-1]]
    num = np.reshape(np.array(num), (len(num)/2, 2))
    ax.imshow(image)
    p = PatchCollection([Polygon(num, closed=True)], facecolor='red', linewidths=0, alpha=1)
    ax.add_collection(p)
    plt.show()
