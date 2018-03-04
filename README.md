# COCO-Style-Dataset-Generator-GUI
This is a simple GUI-based Widget based on matplotlib in Python to facilitate quick and efficient crowd-sourced generation of annotation masks and bounding boxes using a simple interactive User Interface. Optionally, one could choose to use a pretrained Mask RCNN model to come up with initial segmentations. This shifts the work load from painstakingly annotating all the objects in every image to altering wrong predictions made by the system which maybe simpler once an efficient model is learnt.

##### REQUIREMENTS:

`Python 3.5+` is required to run the Mask RCNN code. If only the GUI tool is used, `Python2.7` or `Python3.5+` can be used.

############### Installing Dependencies:

Before running the code, install required pre-requisite python packages using pip.

```
pip install -r requirements.txt
```

##### RUN THE SEGMENTOR GUI:

```
python3 segment.py -i images/
```

##### SEGMENTATION GUI CONTROLS:

![Segmentation GUI Demo with Mask RCNN predictions on pretrained model.](https://github.com/hanskrupakar/COCO-Style-Dataset-Generator-GUI/blob/master/gui.png)

