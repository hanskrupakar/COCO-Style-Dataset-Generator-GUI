from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from matplotlib.widgets import RadioButtons
from matplotlib.path import Path

from PIL import Image
import matplotlib

import argparse
import numpy as np
import glob
import os

from matplotlib.widgets import Button
from matplotlib.lines import Line2D
from matplotlib.artist import Artist

from poly_editor import PolygonInteractor

from matplotlib.mlab import dist_point_to_segment
import sys
from visualize_dataset import return_info

class COCO_dataset_generator(object):

    def __init__(self, fig, ax, args):

        self.ax = ax
        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])

        self.img_dir = args['image_dir']
        self.index = 0
        self.fig = fig
        self.polys = []
        self.zoom_scale, self.points, self.prev, self.submit_p, self.lines, self.circles = 1.2, [], None, None, [], []

        self.zoom_id = fig.canvas.mpl_connect('scroll_event', self.zoom)
        self.click_id = fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.clickrel_id = fig.canvas.mpl_connect('button_release_event', self.onclick_release)
        self.keyboard_id = fig.canvas.mpl_connect('key_press_event', self.onkeyboard)

        self.axradio = plt.axes([0.0, 0.0, 0.2, 1])
        self.axbringprev = plt.axes([0.3, 0.05, 0.17, 0.05])
        self.axreset = plt.axes([0.48, 0.05, 0.1, 0.05])
        self.axsubmit = plt.axes([0.59, 0.05, 0.1, 0.05])
        self.axprev = plt.axes([0.7, 0.05, 0.1, 0.05])
        self.axnext = plt.axes([0.81, 0.05, 0.1, 0.05])
        self.b_bringprev = Button(self.axbringprev, 'Bring Previous Annotations')
        self.b_bringprev.on_clicked(self.bring_prev)
        self.b_reset = Button(self.axreset, 'Reset')
        self.b_reset.on_clicked(self.reset)
        self.b_submit = Button(self.axsubmit, 'Submit')
        self.b_submit.on_clicked(self.submit)
        self.b_next = Button(self.axnext, 'Next')
        self.b_next.on_clicked(self.next)
        self.b_prev = Button(self.axprev, 'Prev')
        self.b_prev.on_clicked(self.previous)

        self.button_axes = [self.axbringprev, self.axreset, self.axsubmit, self.axprev, self.axnext, self.axradio]

        self.existing_polys = []
        self.existing_patches = []
        self.selected_poly = False
        self.objects = []
        self.feedback = args['feedback']

        self.right_click = False

        self.text = ''

        with open(args['class_file'], 'r') as f:
            self.class_names = [x.strip() for x in f.readlines()]

        self.radio = RadioButtons(self.axradio, self.class_names)
        self.class_names = ('BG',) + tuple(self.class_names)

        self.img_paths = sorted(glob.glob(os.path.join(self.img_dir, '*.jpg')))

        if len(self.img_paths)==0:
            self.img_paths = sorted(glob.glob(os.path.join(self.img_dir, '*.png')))
        if os.path.exists(self.img_paths[self.index][:-3]+'txt'):
            self.index = len(glob.glob(os.path.join(self.img_dir, '*.txt')))
        self.checkpoint = self.index
        im = Image.open(self.img_paths[self.index])
        width, height = im.size
        im.close()

        image = plt.imread(self.img_paths[self.index])

        if args['feedback']:

            sys.path.append(args['maskrcnn_dir'])
            import model as modellib
            from demo import BagsConfig
            
            #from skimage.measure import find_contours
            from contours import find_contours

            from visualize_cv2 import random_colors
            
            config = BagsConfig(len(self.class_names)-2)
            
            # Create model object in inference mode.
            model = modellib.MaskRCNN(mode="inference", model_dir='/'.join(args['weights_path'].split('/')[:-2]), config=config)

            # Load weights trained on MS-COCO
            model.load_weights(args['weights_path'], by_name=True)

            r = model.detect([image], verbose=0)[0]

            # Number of instances
            N = r['rois'].shape[0]

            masks = r['masks']

            # Generate random colors
            colors = random_colors(N)

            # Show area outside image boundaries.
            height, width = image.shape[:2]

            class_ids, scores = r['class_ids'], r['scores']

            for i in range(N):
                color = colors[i]

                # Label
                class_id = class_ids[i]
                score = scores[i] if scores is not None else None
                label = self.class_names[class_id]

                # Mask
                mask = masks[:, :, i]

                # Mask Polygon
                # Pad to ensure proper polygons for masks that touch image edges.
                padded_mask = np.zeros(
                    (mask.shape[0] + 2, mask.shape[1] + 2), dtype=np.uint8)
                padded_mask[1:-1, 1:-1] = mask
                contours = find_contours(padded_mask, 0.5)
                
                for verts in contours:
                    # Subtract the padding and flip (y, x) to (x, y)

                    verts = np.fliplr(verts) - 1
                    pat = PatchCollection([Polygon(verts, closed=True)], facecolor='green', linewidths=0, alpha=0.6)
                    self.ax.add_collection(pat)
                    self.objects.append(label)
                    self.existing_patches.append(pat)
                    self.existing_polys.append(Polygon(verts, closed=True, alpha=0.25, facecolor='red'))

        self.ax.imshow(image, aspect='auto')

        self.text+=str(self.index)+'\n'+os.path.abspath(self.img_paths[self.index])+'\n'+str(width)+' '+str(height)+'\n\n'

    def bring_prev(self, event):

        if not self.feedback:

            poly_verts, self.objects = return_info(self.img_paths[self.index-1][:-3]+'txt')

            for num in poly_verts:
                self.existing_polys.append(Polygon(num, closed=True, alpha=0.5, facecolor='red'))

                pat = PatchCollection([Polygon(num, closed=True)], facecolor='green', linewidths=0, alpha=0.6)
                self.ax.add_collection(pat)
                self.existing_patches.append(pat)

    def points_to_polygon(self):
        return np.reshape(np.array(self.points), (int(len(self.points)/2), 2))

    def deactivate_all(self):
        self.fig.canvas.mpl_disconnect(self.zoom_id)
        self.fig.canvas.mpl_disconnect(self.click_id)
        self.fig.canvas.mpl_disconnect(self.clickrel_id)
        self.fig.canvas.mpl_disconnect(self.keyboard_id)

    def onkeyboard(self, event):

        if not event.inaxes:
            return
        elif event.key == 'a':

            if self.selected_poly:
                self.points = self.interactor.get_polygon().xy.flatten()
                self.interactor.deactivate()
                self.right_click = True
                self.selected_poly = False
                self.fig.canvas.mpl_connect(self.click_id, self.onclick)
                self.polygon.color = (0,255,0)
                self.fig.canvas.draw()
            else:
                for i, poly in enumerate(self.existing_polys):

                    if poly.get_path().contains_point((event.xdata, event.ydata)):

                        self.radio.set_active(self.class_names.index(self.objects[i])-1)
                        self.polygon = self.existing_polys[i]
                        self.existing_patches[i].set_visible(False)
                        self.fig.canvas.mpl_disconnect(self.click_id)
                        self.ax.add_patch(self.polygon)
                        self.fig.canvas.draw()
                        self.interactor = PolygonInteractor(self.ax, self.polygon)
                        self.selected_poly = True
                        self.existing_polys.pop(i)
                        break

        elif event.key == 'r':

            for i, poly in enumerate(self.existing_polys):
                if poly.get_path().contains_point((event.xdata, event.ydata)):
                    self.existing_patches[i].set_visible(False)
                    self.existing_patches[i].remove()
                    self.existing_patches.pop(i)
                    self.existing_polys.pop(i)
                    break
        self.fig.canvas.draw()

    def next(self, event):

        if len(self.text.split('\n'))>5:

            print (self.img_paths[self.index][:-3]+'txt')

            with open(self.img_paths[self.index][:-3]+'txt', "w") as text_file:
                text_file.write(self.text)

        self.ax.clear()

        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])

        if (self.index<len(self.img_paths)-1):
            self.index += 1
        else:
            exit()

        image = plt.imread(self.img_paths[self.index])
        self.ax.imshow(image, aspect='auto')

        im = Image.open(self.img_paths[self.index])
        width, height = im.size
        im.close()

        self.reset_all()

        self.text+=str(self.index)+'\n'+os.path.abspath(self.img_paths[self.index])+'\n'+str(width)+' '+str(height)+'\n\n'

    def reset_all(self):

        self.polys = []
        self.text = ''
        self.points, self.prev, self.submit_p, self.lines, self.circles = [], None, None, [], []

    def previous(self, event):

        if (self.index>self.checkpoint):
            self.index-=1
        #print (self.img_paths[self.index][:-3]+'txt')
        os.remove(self.img_paths[self.index][:-3]+'txt')

        self.ax.clear()

        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])

        image = plt.imread(self.img_paths[self.index])
        self.ax.imshow(image, aspect='auto')

        im = Image.open(self.img_paths[self.index])
        width, height = im.size
        im.close()

        self.reset_all()

        self.text+=str(self.index)+'\n'+os.path.abspath(self.img_paths[self.index])+'\n'+str(width)+' '+str(height)+'\n\n'

    def onclick(self, event):

        if not event.inaxes:
            return
        if not any([x.in_axes(event) for x in self.button_axes]):
            if event.button==1:
                self.points.extend([event.xdata, event.ydata])
                #print (event.xdata, event.ydata)

                circle = plt.Circle((event.xdata,event.ydata),2.5,color='black')
                self.ax.add_artist(circle)
                self.circles.append(circle)

                if (len(self.points)<4):
                    self.r_x = event.xdata
                    self.r_y = event.ydata
            else:
                if len(self.points)>5:
                    self.right_click=True
                    self.fig.canvas.mpl_disconnect(self.click_id)
                    self.click_id = None
                    self.points.extend([self.points[0], self.points[1]])
                    #self.prev.remove()

            if (len(self.points)>2):
                line = self.ax.plot([self.points[-4], self.points[-2]], [self.points[-3], self.points[-1]], 'b--')
                self.lines.append(line)

            self.fig.canvas.draw()

            if len(self.points)>4:
                if self.prev:
                    self.prev.remove()
                self.p = PatchCollection([Polygon(self.points_to_polygon(), closed=True)], facecolor='red', linewidths=0, alpha=0.4)
                self.ax.add_collection(self.p)
                self.prev = self.p

                self.fig.canvas.draw()

            #if len(self.points)>4:
            #    print 'AREA OF POLYGON: ', self.find_poly_area(self.points)
            #print event.x, event.y

    def find_poly_area(self):
        coords = self.points_to_polygon()
        x, y = coords[:,0], coords[:,1]
        return (0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1))))/2 #shoelace algorithm

    def onclick_release(self, event):

        if any([x.in_axes(event) for x in self.button_axes]) or self.selected_poly:
            return

        if hasattr(self, 'r_x') and hasattr(self, 'r_y') and None not in [self.r_x, self.r_y, event.xdata, event.ydata]:
            if np.abs(event.xdata - self.r_x)>10 and np.abs(event.ydata - self.r_y)>10: # 10 pixels limit for rectangle creation
                if len(self.points)<4:

                    self.right_click=True
                    self.fig.canvas.mpl_disconnect(self.click_id)
                    self.click_id = None
                    bbox = [np.min([event.xdata, self.r_x]), np.min([event.ydata, self.r_y]), np.max([event.xdata, self.r_x]), np.max([event.ydata, self.r_y])]
                    self.r_x = self.r_y = None

                    self.points = [bbox[0], bbox[1], bbox[0], bbox[3], bbox[2], bbox[3], bbox[2], bbox[1], bbox[0], bbox[1]]
                    self.p = PatchCollection([Polygon(self.points_to_polygon(), closed=True)], facecolor='red', linewidths=0, alpha=0.4)
                    self.ax.add_collection(self.p)
                    self.fig.canvas.draw()

    def zoom(self, event):

        if not event.inaxes:
            return
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location

        if event.button == 'down':
            # deal with zoom in
            scale_factor = 1 / self.zoom_scale
        elif event.button == 'up':
            # deal with zoom out
            scale_factor = self.zoom_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print (event.button)

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

        self.ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
        self.ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
        self.ax.figure.canvas.draw()

    def reset(self, event):

        if not self.click_id:
            self.click_id = fig.canvas.mpl_connect('button_press_event', self.onclick)
        #print (len(self.lines))
        #print (len(self.circles))
        if len(self.points)>5:
            for line in self.lines:
                line.pop(0).remove()
            for circle in self.circles:
                circle.remove()
            self.lines, self.circles = [], []
            self.p.remove()
            self.prev = self.p = None
            self.points = []
        #print (len(self.lines))
        #print (len(self.circles))

    def print_points(self):

        ret = ''
        for x in self.points:
            ret+='%.2f'%x+' '
        return ret

    def submit(self, event):

        if not self.right_click:
            print ('Right click before submit is a must!!')
        else:

            self.text+=self.radio.value_selected+'\n'+'%.2f'%self.find_poly_area()+'\n'+self.print_points()+'\n\n'
            self.right_click = False
            #print (self.points)

            self.lines, self.circles = [], []
            self.click_id = fig.canvas.mpl_connect('button_press_event', self.onclick)

            self.polys.append(Polygon(self.points_to_polygon(), closed=True, color=np.random.rand(3), alpha=0.4, fill=True))
            if self.submit_p:
                self.submit_p.remove()
            self.submit_p = PatchCollection(self.polys, cmap=matplotlib.cm.jet, alpha=0.4)
            self.ax.add_collection(self.submit_p)
            self.points = []

if __name__=='__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image_dir", required=True, help="Path to the image dir")
    ap.add_argument("-c", "--class_file", required=True, help="Path to the classes file of the dataset")
    ap.add_argument("-f", "--feedback", required=False, help="Whether or not to include AI feedback", action='store_true')
    ap.add_argument('-p', "--maskrcnn_dir", default='/home/hans/Desktop/Vision Internship/Mask_RCNN/', help="Path to Mask RCNN Repo")
    ap.add_argument('-w', "--weights_path", default='/home/hans/Desktop/Vision Internship/Mask_RCNN/logs/imagenet_10/mask_rcnn_bags_0006.h5', help="Path to Mask RCNN checkpoint save file")
    args = vars(ap.parse_args())

    fig = plt.figure(figsize=(14, 14))
    ax = plt.gca()

    gen = COCO_dataset_generator(fig, ax, args)

    plt.subplots_adjust(bottom=0.2)
    plt.show()

    gen.deactivate_all()
