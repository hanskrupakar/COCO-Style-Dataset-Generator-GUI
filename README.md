# COCO-Style-Dataset-Generator-GUI

This is a simple GUI-based Widget based on matplotlib in Python to facilitate quick and efficient crowd-sourced generation of annotation masks and bounding boxes using a simple interactive User Interface. Annotation can be in terms of polygon points covering all parts of an object (see instructions in README) or it can simply be a bounding box, for which you click and drag the mouse button. Optionally, one could choose to use a pretrained Mask RCNN model to come up with initial segmentations. This shifts the work load from painstakingly annotating all the objects in every image to altering wrong predictions made by the system which maybe simpler once an efficient model is learnt.

#### Note: This repo only contains code to annotate every object using a single polygon figure. Support for multi-polygon objects and `iscrowd=True` annotations isn't available yet. Feel free to extend the repo as you wish. Also, the code uses xyxy bounding boxes while coco uses xywh; something to keep in mind if you intend to create a custom COCO dataset to plug into other models as COCO datasets.

### REQUIREMENTS:

`Python 3.5+` is required to run the Mask RCNN code. If only the GUI tool is used, `Python2.7` or `Python3.5+` can be used.

###### NOTE: For python2.7, OpenCV needs to be installed from source and configured to be in the environment running the code.
###### Before installing, please upgrade setuptools using: pip install --upgrade setuptools
###### For Windows users, please install Visual Studio C++ 14 or higher if necessary using this link: http://go.microsoft.com/fwlink/?LinkId=691126&fixForIE=.exe. 

### RUN THE SEGMENTOR GUI:

Clone the repo.

```
git clone https://github.com/hanskrupakar/COCO-Style-Dataset-Generator-GUI.git
```

#### Installing Dependencies:

Before running the code, install required pre-requisite python packages using pip.

If you wish to use Mask RCNN to prelabel based on a trained model, please use the environment variable `MASK_RCNN="y"`, otherwise there's no need to include it and you could just perform the install.

###### Without Mask RCNN

```
cd COCO-Style-Dataset-Generator-GUI/
python setup.py install
```

###### With Mask RCNN

```
cd COCO-Style-Dataset-Generator-GUI/
MASK_RCNN="y" python3 setup.py install
```

#### Running the instance segmentation GUI without Mask RCNN pretrained predictions:

In a separate text file, list the target labels/classes line-by-line to be displayed along with the dataset for class labels. For example, look at [classes/products.txt](https://github.com/hanskrupakar/COCO-Style-Dataset-Generator-GUI/blob/master/classes/products.txt)

```
python3 -m coco_dataset_generator.gui.segment -i background/ -c classes/products.txt

python3 -m coco_dataset_generator.gui.segment_bbox_only -i background/ -c classes/products.txt
```

#### Running the instance segmentation GUI augmented by initial Mask RCNN pretrained model predictions:

To run the particular model for the demo, download the pretrained weights from [HERE!!!](https://drive.google.com/file/d/1GaKVP3BvTfMwPbhEm4nF7fLATV-eDkFQ/view?usp=sharing). Download and extract pretrained weights into the repository.

```
python3 -m coco_dataset_generator.gui.segment -i background/ -c classes/products.txt \
                                              -w <MODEL_FILE> [--config <CONFIG_FILE>]

python3 -m coco_dataset_generator.gui.segment_bbox_only -i background/ -c classes/products.txt \
                                              -w <MODEL_FILE> [--config <CONFIG_FILE>]
```

The configuration file for Mask RCNN becomes relevant when you play around with the configuration parameters that make up the network. In order to seamlessly use the repository with multiple such Mask RCNN models for different types of datasets, you could create a single config file for every project and use them as you please. The base repository has been configured to work well with the demo model provided and so any change to the parameters should be followed by generation of its corresponding config file.

HINT: Use `get_json_config.py` inside `Mask RCNN` to get config file wrt specific parameters of Mask RCNN. You could either clone [Mask_RCNN](https://www.github.com/hanskrupakar/Mask_RCNN), use `pip install -e Mask_RCNN/` to replace the mask_rcnn installed from this repo and then get access to `get_json_config.py` easily or you could find where pip installs `mask_rcnn` and find it directly from the source.

`USAGE: segment.py [-h] -i IMAGE_DIR -c CLASS_FILE [-w WEIGHTS_PATH] [-x CONFIG_PATH]`

`USAGE: segment_bbox_only.py [-h] -i IMAGE_FILE -c CLASSES_FILE [-j JSON_FILE] [--save_csv] [-w WEIGHTS_PATH] [-x CONFIG_PATH]`

##### Optional Arguments

| Shorthand       | Flag Name                   | Description                                                                        |
| --------------- | --------------------------- | ---------------------------------------------------------------------------------- |
| -h              | --help                      | Show this help message and exit                                                    |
| -i IMAGE_DIR    | --image_dir IMAGE_DIR       | Path to the image dir                                                              |
| -c CLASS_FILE   | --class_file CLASS_FILE     | Path to object labels                                                              |
| -w WEIGHTS_PATH | --weights_path WEIGHTS_PATH | Path to Mask RCNN checkpoint save file                                             |
| -j JSON_FILE    | --json_file JSON_FILE       | Path of JSON file to append dataset to                                             |
|                 | --save_csv                  | Choose option to save dataset as CSV file                                          |
| -x CONFIG_FILE  | --config_file CONFIG_FILE   | Path of JSON file for training config; Use `get_json_config` script from Mask RCNN |

### POLYGON SEGMENTATION GUI CONTROLS:

![deepmagic](https://github.com/Deep-Magic/COCO-Style-Dataset-Generator-GUI/blob/master/gui.png)

In this demo, all the green patches over the objects are the rough masks generated by a pretrained Mask RCNN network.

Key-bindings/
Buttons

EDIT MODE (when `a` is pressed and polygon is being edited)

      'a'       toggle vertex markers on and off.
                When vertex markers are on, you can move them, delete them

      'd'       delete the vertex under point

      'i'       insert a vertex at point near the boundary of the polygon.

    Left click  Use on any point on the polygon boundary and move around
                by dragging to alter shape of polygon

REGULAR MODE

    Scroll Up       Zoom into image

    Scroll Down     Zoom out of image

    Left Click      Create a point for a polygon mask around an object

    Right Click     Complete the polygon currently formed by connecting all selected points

    Left Click Drag Create a bounding box rectangle from point 1 to point 2 (works only
                    when there are no polygon points on screen for particular object)

      'a'           Press key on top of overlayed polygon (from Mask RCNN or
                    previous annotations) to select it for editing

      'r'           Press key on top of overlayed polygon (from Mask RCNN or
                    previous annotations) to completely remove it

    BRING PREVIOUS ANNOTATIONS  Bring back the annotations from the previous image to preserve
                                similar annotations.

    SUBMIT                      To be clicked after Right click completes polygon! Finalizes current
                                segmentation mask and class label picked.
                                After this, the polygon cannot be edited.

    NEXT                        Save all annotations created for current file and move on to next image.

    PREV                        Goto previous image to re-annotate it. This deletes the annotations
                                created for the file before the current one in order to
                                rewrite the fresh annotations.

    RESET                       If when drawing the polygon using points, the polygon doesn't cover the
                                object properly, reset will let you start fresh with the current polygon.
                                This deletes all the points on the image.

The green annotation boxes from the network can be edited by pressing on the Keyboard key `a` when the mouse pointer is on top of a particular such mask. Once you press `a`, the points making up that polygon will show up and you can then edit it using the key bindings specified. Once you're done editing the polygon, press `a` again to finalize the edits. At this point, it will become possible to submit that particular annotation and move on to the next one.

Once the GUI tool has been used successfully and relevant txt files have been created for all annotated images, one can use `create_json_file.py` to create the COCO-Style JSON file.

```
python -m coco_dataset_generator.utils.create_json_file -i background/ -c classes/products.txt
                                        -o output.json -t jpg
```

```
USAGE: create_json_file.py [-h] -i IMAGE_DIR -o FILE_PATH -c CLASS_FILE -t TYPE
```

##### Optional Arguments

| Shorthand     | Flag Name               | Description                             |
| ------------- | ----------------------- | --------------------------------------- |
| -i IMAGE_DIR  | --image_dir IMAGE_DIR   | Path to the image dir                   |
| -o FILE_PATH  | --file_path FILE_PATH   | Path of output file                     |
| -c CLASS_FILE | --class_file CLASS_FILE | Path of file with output classes        |
| -t TYPE       | --type TYPE             | Type of the image files (jpg, png etc.) |

### RECTANGULAR BOUNDING BOX GUI CONTROLS:

The same GUI is designed slightly differently in case of rectangular bounding box annotations with speed of annotation in mind. Thus, most keys are keyboard bindings. Most ideally, this interface is very suited to serve to track objects across video by dragging around a box of similar size. Since the save button saves multiple frame results together, the JSON file is directly created instead of txt files for each image, which means there wouldn't be a need to use `create_json_file.py`.

Key-bindings/
Buttons

EDIT MODE (when `a` is pressed and rectangle is being edited)

      'a'       toggle vertex markers on and off.  When vertex markers are on,
                you can move them, delete them

      'i'       insert rectangle in the list of final objects to save.

    Left click  Use on any point on the rectangle boundary and move around by
                dragging to alter shape of rectangle

REGULAR MODE

    Scroll Up       Zoom into image

    Scroll Down     Zoom out of image

    Left Click Drag Create a bounding box rectangle from point 1 to point 2.

      'a'           Press key on top of overlayed polygon (from Mask RCNN or
                    previous annotations) to select it for editing

      'r'           Press key on top of overlayed polygon (from Mask RCNN or
                    previous annotations) to completely remove it

      'n'           Press key to move on to next image after completing all
                    rectangles in current image

      SAVE          Save all annotated objects so far

### LIST OF FUNCTIONALITIES:

        FILE                            FUNCTIONALITY

    cut_objects.py                  Cuts objects based on bounding box annotations using dataset.json
                                    file and creates occlusion-based augmented images dataset.

    create_json_file.py             Takes a directory of annotated images (use segment.py to annotate
                                    into text files) and returns a COCO-style JSON file.

    extract_frames.py               Takes a directory of videos and extracts all the frames of all
                                    videos into a folder labeled adequately by the video name.

    pascal_to_coco.py               Takes a PASCAL-style dataset directory with JPEGImages/ and
                                    Annotations/ folders and uses the bounding box as masks to
                                    create a COCO-style JSON file.

    segment.py                      Read the instructions above.

    segment_bbox_only.py            Same functionality but optimized for easier annotation of
                                    bbox-only datasets.

    test_*.py                       Unit tests.

    visualize_dataset.py            Visualize the annotations created using the tool.

    visualize_json_file.py          Visualize the dataset JSON file annotations on the entire dataset.

    compute_dataset_statistics.py   Find distribution of objects in the dataset by counts.

    combine_json_files.py           Combine different JSON files together into a single dataset file.

    delete_images.py                Delete necessary images from the JSON dataset.

NOTE: Please use `python <FILENAME>.py -h` for details on how to use each of the above files.
