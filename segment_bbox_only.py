from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from matplotlib.widgets import RadioButtons
from matplotlib.path import Path
import matplotlib.patches as patches

from skimage.measure import find_contours

from PIL import Image
import matplotlib

import argparse
import numpy as np
import glob
import os
from matplotlib.widgets import RectangleSelector, Button, RadioButtons
from matplotlib.lines import Line2D
from matplotlib.artist import Artist

from poly_editor import PolygonInteractor

from matplotlib.mlab import dist_point_to_segment
import sys
from visualize_dataset import return_info

import json

from collections import defaultdict


def read_JSON_file(f):
    
    with open(f, 'r') as g:
        d = json.loads(g.read())
    
    img_paths = [x['file_name'] for x in d['images']]
    
    rects = [{'bbox': x['segmentation'][0], 'class': x['category_id'], 'image_id': x['image_id']} for x in d['annotations']]
    
    annotations = defaultdict(list)
    
    for rect in rects:
        r = rect['bbox']
        x0, y0 = min(r[0], r[2], r[4], r[6]), min(r[1], r[3], r[5], r[7])
        x1, y1 = max(r[0], r[2], r[4], r[6]), max(r[1], r[3], r[5], r[7])
        
        r = patches.Rectangle((x0,y0),x1-x0,y1-y0,linewidth=1,edgecolor='g',facecolor='g', alpha=0.4)        
        
        annotations[img_paths[rect['image_id']]].append({'bbox': r, 'cls': d['classes'][rect['class']-1]})
        
    return d['classes'], img_paths, annotations


class COCO_dataset_generator(object): 
    
    def __init__(self, fig, ax, img_dir, classes, model_path, json_file):
    
        self.RS = RectangleSelector(ax, self.line_select_callback,
                                       drawtype='box', useblit=True,
                                       button=[1, 3],  # don't use middle button
                                       minspanx=5, minspany=5,
                                       spancoords='pixels',
                                       interactive=True) 
                                         
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        
        #self.classes, self.img_paths, _ = read_JSON_file(json_file)
        with open(classes, 'r') as f:
            self.classes, img_paths = sorted([x.strip().split(',')[0] for x in f.readlines()]), glob.glob(os.path.abspath(os.path.join(img_dir, '*.jpg')))
        plt.tight_layout()

        self.ax = ax
        self.fig = fig
        self.axradio = plt.axes([0.0, 0.0, 0.1, 1])
        self.radio = RadioButtons(self.axradio, self.classes)
        self.zoom_scale = 1.2
        self.zoom_id = self.fig.canvas.mpl_connect('scroll_event', self.zoom) 
        self.keyboard_id = self.fig.canvas.mpl_connect('key_press_event', self.onkeyboard)
        self.selected_poly = False
        self.axsave = plt.axes([0.81, 0.05, 0.1, 0.05])
        self.b_save = Button(self.axsave, 'Save')
        self.b_save.on_clicked(self.save)        
        self.objects, self.existing_patches, self.existing_rects = [], [], []
        self.num_pred = 0
        if json_file is None:
            self.images, self.annotations = [], [] 
            self.index = 0
            self.ann_id = 0
        else:
            with open(json_file, 'r') as g:
                d = json.loads(g.read())
            self.images, self.annotations = d['images'], d['annotations']
            self.index = len(self.images)
            self.ann_id = len(self.annotations)
        print (self.index)
        prev_files = [x['file_name'] for x in self.images]
        for i, f in enumerate(img_paths):
            im = Image.open(f)
            width, height = im.size
            dic = {'file_name': f, 'id': self.index+i, 'height': height, 'width': width} 
            if f not in prev_files:
                self.images.append(dic)
            else:
                self.index+=1
        image = plt.imread(self.images[self.index]['file_name'])
        self.ax.imshow(image, aspect='auto')

        if not args['no_feedback']:
            sys.path.append(args['maskrcnn_dir'])
            from config import Config
            import model as modellib
            from skimage.measure import find_contours
            from visualize_cv2 import random_colors
        
            class InstanceConfig(Config):
                NAME = os.path.basename(model_path)
                GPU_COUNT = 1
                IMAGES_PER_GPU = 1
                NUM_CLASSES = 22 + 1
                IMAGE_SHAPE = np.array([Config.IMAGE_MIN_DIM, Config.IMAGE_MIN_DIM, 3])
            self.config = InstanceConfig()
        
            plt.connect('draw_event', self.persist)
        
            # Create model object in inference mode.
            self.model = modellib.MaskRCNN(mode="inference", model_dir='/'.join(args['weights_path'].split('/')[:-2]), config=self.config)

            # Load weights trained on MS-COCO
            self.model.load_weights(args['weights_path'], by_name=True)
        
            r = self.model.detect([image], verbose=0)[0]
     
            # Number of instances
            N = r['rois'].shape[0]
        
            masks = r['masks']
        
            # Show area outside image boundaries.
            height, width = image.shape[:2]
        
            class_ids, scores, rois = r['class_ids'], r['scores'], r['rois'],
       
            for i in range(N):
            
                # Label
                class_id = class_ids[i]
                score = scores[i] if scores is not None else None
                label = self.classes[class_id-1]
                pat = patches.Rectangle((rois[i][1], rois[i][0]), rois[i][3]-rois[i][1], rois[i][2]-rois[i][0], linewidth=1, edgecolor='r',facecolor='r', alpha=0.4)
                rect = self.ax.add_patch(pat)
                        
                self.objects.append(label)
                self.existing_patches.append(pat.get_bbox().get_points())
                self.existing_rects.append(pat)
            self.num_pred = len(self.objects)
    
    def line_select_callback(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
    
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

    def save(self, event):
        if len(self.objects) == 0:
            data = {'images':self.images[:self.index+1], 'annotations':self.annotations, 'categories':[], 'classes': self.classes}

        with open('output.json', 'w') as outfile:
            json.dump(data, outfile)
    
    def persist(self, event):
        if self.RS.active:
            self.RS.update()
        
    def onkeyboard(self, event):
        
        if not event.inaxes:
            return
        elif event.key == 'a':
            for i, ((xmin, ymin), (xmax, ymax)) in enumerate(self.existing_patches):
                if xmin<=event.xdata<=xmax and ymin<=event.ydata<=ymax:
                    self.radio.set_active(self.classes.index(self.objects[i]))
                    self.RS.set_active(True)
                    self.rectangle = self.existing_rects[i]
                    self.rectangle.set_visible(False)
                    coords = self.rectangle.get_bbox().get_points()
                    self.RS.extents = [coords[0][0], coords[1][0], coords[0][1], coords[1][1]]
                    self.RS.to_draw.set_visible(True)
                    self.fig.canvas.draw()
                    self.existing_rects.pop(i)
                    self.existing_patches.pop(i)
                    self.objects.pop(i)
                    fig.canvas.draw()
                    break
            
        elif event.key == 'i':
            b = self.RS.extents # xmin, xmax, ymin, ymax
            b = [int(x) for x in b]
            if b[1]-b[0]>0 and b[3]-b[2]>0:
                poly = [b[0], b[2], b[0], b[3], b[1], b[3], b[1], b[2], b[0], b[2]]
                area = (b[1]-b[0])*(b[3]-b[2])
                bbox = [b[0], b[2], b[1], b[3]]
                dic2 = {'segmentation': poly, 'area': area, 'iscrowd':0, 'image_id':self.index, 'bbox':bbox, 'category_id': self.classes.index(self.radio.value_selected)+1, 'id': self.ann_id}
                if dic2 not in self.annotations:
                    self.annotations.append(dic2)
                self.ann_id+=1
                rect = patches.Rectangle((b[0],b[2]),b[1]-b[0],b[3]-b[2],linewidth=1,edgecolor='g',facecolor='g', alpha=0.4)
                self.ax.add_patch(rect)
                
                self.RS.set_active(False)
                
                self.fig.canvas.draw()
                self.RS.set_active(True)
        elif event.key in ['N', 'n']:
            self.ax.clear()
            self.index+=1
            if (len(self.objects)==self.num_pred):
                self.images.pop(self.index-1)
                self.index-=1
            print(self.index)
            print (self.images)
            if self.index==len(self.images):
                exit()
            image = plt.imread(self.images[self.index]['file_name'])
            self.ax.imshow(image)
            self.ax.set_yticklabels([])
            self.ax.set_xticklabels([])
            r = self.model.detect([image], verbose=0)[0]
     
            # Number of instances
            N = r['rois'].shape[0]
        
            masks = r['masks']
        
            # Show area outside image boundaries.
            height, width = image.shape[:2]
        
            class_ids, scores, rois = r['class_ids'], r['scores'], r['rois'],
            self.existing_rects, self.existing_patches, self.objects = [], [], []
            for i in range(N):
                
                # Label
                class_id = class_ids[i]
                score = scores[i] if scores is not None else None
                label = self.classes[class_id-1]
                pat = patches.Rectangle((rois[i][1], rois[i][0]), rois[i][3]-rois[i][1], rois[i][2]-rois[i][0], linewidth=1, edgecolor='r',facecolor='r', alpha=0.4)
                rect = self.ax.add_patch(pat)
                        
                self.objects.append(label)

                self.existing_patches.append(pat.get_bbox().get_points())
                self.existing_rects.append(pat)
            
            self.num_pred = len(self.objects)
            self.fig.canvas.draw()
            
        elif event.key in ['q','Q']:
            exit()
    
if __name__=='__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image_file", required=True, help="Path to the images dir")
    ap.add_argument("-c", "--classes_file", required=True, help="Path to classes file") 
    ap.add_argument("-j", "--json_file", required=False, help="Path of JSON file to append dataset to", default=None)
    ap.add_argument("--save_csv", required=False, action="store_true", help="Choose option to save dataset as CSV file annotations.csv")
    ap.add_argument("-n", "--no_feedback", required=False, help="Whether or not to include AI feedback", action='store_true')
    ap.add_argument('-p', "--maskrcnn_dir", default='/home/hans/Desktop/Vision Internship/Mask_RCNN/', help="Path to Mask RCNN Repo")
    ap.add_argument('-w', "--weights_path", default='/home/hans/Desktop/Vision Internship/Mask_RCNN/logs/mask_rcnn_overfit3.h5', help="Path to Mask RCNN checkpoint save file")
    args = vars(ap.parse_args())
    
    
    fig = plt.figure(figsize=(14, 14))
    ax = plt.gca()
    
    gen = COCO_dataset_generator(fig, ax, args['image_file'], args['classes_file'], args['weights_path'], args['json_file'])
    
    plt.subplots_adjust(bottom=0.2)
    plt.show()
