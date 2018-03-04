from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

import argparse
import numpy as np

zoom_scale, points, objects, prev = 1.2, [], [], None

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())
 
fig = plt.figure(figsize=(14, 14))
ax = plt.gca()
image = plt.imread(args["image"])

def zoom(event):

    global zoom_scale, ax, fig

    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()

    xdata = event.xdata # get event x location
    ydata = event.ydata # get event y location

    if event.button == 'down':
        # deal with zoom in
        scale_factor = 1 / zoom_scale
    elif event.button == 'up':
        # deal with zoom out
        scale_factor = zoom_scale
    else:
        # deal with something that should never happen
        scale_factor = 1
        print event.button

    new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

    relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
    rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

    ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
    ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
    ax.figure.canvas.draw()

   
plt.imshow(image, aspect='auto')
zoom_id = fig.canvas.mpl_connect('scroll_event', zoom)
#click_id = fig.canvas.mpl_connect('button_press_event', onclick)

#plt.subplots_adjust(bottom=0.2)
plt.axis('off')
plt.show()

fig.canvas.mpl_disconnect(zoom_id)
#fig.canvas.mpl_disconnect(click_id)
