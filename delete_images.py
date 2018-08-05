import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def press(event):
    
    if event.key.lower() == 'q':
        exit()
    
    if event.key.lower() == 'd':
        del new_imgs[ptr]
        for ann in anns:
            new_anns.remove(ann)
        print ('Deleted image:', new_imgs[ptr]["file_name"], "from the dataset!")
            
    if event.key.lower() == 'j':
        print ("Saving dataset to file! Please wait!")
        
        # Account for deletions by changing label space
        
        id_list = [int(img['id']) for img in new_imgs]
        ann_list = [int(ann['id']) for ann in new_anns]
        
        full_img, full_ann = [x for x in range(len(id_list))], [x for x in range(len(ann_list))]
        
        free_img, free_ann = list(set(full_img)-set(id_list)), list(set(full_ann)-set(ann_list))
        change_img, change_ann = list(set(id_list)-set(full_img)), list(set(ann_list)-set(full_ann))
        
        for f, c in zip(free_img, change_img):
            for img in new_imgs:
                if img['id']==c:
                    img['id']=f
            for ann in new_anns:
                if ann['image_id']==c:
                    ann['image_id']=f
        
        for f, c in zip(free_ann, change_ann):
            for ann in new_anns:
                if ann['id']==c:
                    ann['id']=f
        
        data = {'images': new_imgs, 'annotations': new_anns, 'categories':[], 'classes':classes}
        with open('deleted_dataset.json', 'w') as f:
            json.dump(data, f)
        print ("Dataset saved!")
    else:      
        plt.close()
    
    
if __name__=='__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument('--json_file', required=True, help='Path to JSON file')
    args = ap.parse_args()
    
    with open(args.json_file, 'r') as f:
        obj = json.load(f)
    
    images, annotations = obj["images"], obj["annotations"]
    classes = obj["classes"]
    
    print ("Total number of images in dataset: ", len(images))
    
    new_imgs, new_anns = images, annotations
    
    for ptr, img in enumerate(images):
        
        fig, ax = plt.subplots()
        plt.tick_params(axis='both', which='both', bottom='off', top='off', 
                    labelbottom='off', right='off', left='off', labelleft='off')
    
        fig.canvas.mpl_connect('key_press_event', press)
        ax.set_title('d - Delete image; j - Save dataset; q - Exit; others - Next image')
    
        anns = [ann for ann in annotations if ann["image_id"]==img["id"]]
        image = plt.imread(img["file_name"])
        plt.imshow(image)
        for ann in anns:
            s = [int(x) for x in ann['bbox']]
            rect = patches.Rectangle((s[0],s[1]),s[2]-s[0],s[3]-s[1],linewidth=1,edgecolor='r',facecolor='none')
            ax = plt.gca()
            ax.add_patch(rect)
            plt.text(s[0]-10, s[1]+10, classes[ann['category_id']-1])
        plt.show()
    
    print ("Saving dataset to file! Please wait!")
    data = {'images': new_imgs, 'annotations': new_anns, 'categories':[], 'classes':classes}
    with open('deleted_dataset.json', 'w') as f:
        json.dump(data, f)
    print ("Dataset saved!")
