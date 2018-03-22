import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

def cut_bbox(rect):

    x = np.linspace(rect[0], rect[2], num=50)
    y = (rect[3]+rect[1])/2 + 15*np.sin(x/(500/np.pi/2))
    
    x1 = np.concatenate((x, np.array([rect[2], rect[0]])))
    y1 = np.concatenate((y, np.array([rect[3], rect[3]])))
    
    x2 = np.concatenate((x, np.array([rect[2], rect[0]])))
    y2 = np.concatenate((y, np.array([rect[1], rect[1]])))
    
    poly1 = [(x,y) for x,y in zip(x1, y1)]
    poly2 = [(x,y) for x,y in zip(x2, y2)]
    
    return poly1, poly2

print (cut_bbox([50, 100, 500, 500]))
