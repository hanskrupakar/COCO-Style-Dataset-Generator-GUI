'''
USAGE:
python combine_json_files.py <LIST OF FILES>
'''

import json
import glob
import sys

if __name__=='__main__':
	
	if len(sys.argv) < 3:
		print ("Not enough input files to combine into a single dataset file")
		exit()
		
	
	files = sys.argv[1:]
	
	img_counter = 0
	ann_counter = 0
	
	combined_obj = None
	
	for file_path in files:
		
		with open(file_path, 'r') as f:
			obj = json.loads(f.read())
		
		for img in obj["images"]:
			img["id"] += img_counter
		
		for ann in obj["annotations"]:
			ann["id"] += ann_counter
			ann["image_id"] += img_counter
		
		ann_counter += len(obj["annotations"])
		img_counter += len(obj["images"])
		
		if combined_obj is None:
			combined_obj = obj
		else:
			if combined_obj["classes"] != obj["classes"]:
				print ("Dataset mismatch between the JSON files!")
				exit()
				
			combined_obj["images"].extend(obj["images"])
			combined_obj["annotations"].extend(obj["annotations"])
			combined_obj["categories"].extend(obj["categories"])
	
	with open("merged_json.json", "w") as f:
		json.dump(combined_obj, f)
