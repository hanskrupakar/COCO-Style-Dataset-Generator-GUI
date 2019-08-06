from setuptools import setup, find_packages
import os

def install(package):
    os.system("pip install %s"%(package))

if os.getenv('MASK_RCNN'):
    
    with open('requirements_maskrcnn.txt', 'r') as f:
        packs = [x.strip() for x in f.readlines()]
        
    for p in packs:
        install(p)	
    dependencies = []
else:
    dependencies = [
	"matplotlib==3.0.3",
	"numpy==1.16.4",
	"opencv-python",
    "Pillow",
	"scikit-image",
	"scipy",
	]
	
packages = [
    package for package in find_packages() if package.startswith('coco_dataset_generator')
]

setup(name='coco_dataset_generator',
      version='1.0',
      description='COCO Style Dataset Generator GUI',
      author='hanskrupakar',
      author_email='hansk@nyu.edu',
      license='Open-Source',
      url='https://www.github.com/hanskrupakar/COCO-Style-Dataset-Generator-GUI',
      packages=packages,
      install_requires=dependencies,
      test_suite='unit_tests',
)
