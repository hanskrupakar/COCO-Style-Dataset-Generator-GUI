from setuptools import setup, find_packages
import os
import sys
import subprocess

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

if os.getenv('MASK_RCNN'):
    fl = 'requirements_maskrcnn.txt'
else:
    fl = 'requirements.txt'

with open(fl, 'r') as f:
    packs = [x.strip() for x in f.readlines()]
        
for p in packs:
    install(p)	

dependencies = []
	
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
