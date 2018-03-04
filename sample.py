import glob, os
import shutil

for folder in ['hans_0/*', 'hans_1/*', 'hans_2/*']:
	
	for i, f in enumerate(sorted(glob.glob(folder))):
		if(i%5==0):
			shutil.copyfile(f, folder.split('/')[0]+'-'+f.split('/')[-1])
