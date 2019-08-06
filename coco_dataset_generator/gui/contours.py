from skimage.measure import find_contours as FC
import numpy as np
from simplification.cutil import simplify_coords

def find_contours(*args):
    
    contours = FC(*args)
    
    simplified_contours = [np.array(simplify_coords(x, 1), dtype=np.int32) \
                                for x in contours]
    
    return simplified_contours
        
