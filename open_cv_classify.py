# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 15:24:51 2016

@author: David
"""

import cv2
from sklearn.externals import joblib
from skimage.feature import hog
import numpy as np
import os

def show_image(img):
    cv2.imshow("Image", img)
    cv2.waitKey()
    
def absorb_rect_below(rect1, rect2):
    """
    Given a set of rectangle tuples, combines rectangles that are in veritical alignment
    Rectangle tuples take the form x, y, w, h
    """
    
    combined_rect = (0,0,0,0)
    
    # establish that the lateral distances are similar
    ratio = float(rect1[2]) / rect2[2]
    scale_benchmark = max(rect1[2], rect2[2])

    if not .85 <= ratio <= 1.15:
        return False
       
    # establish that the rectangles are vertically aligned
    x_diff_top_right = abs(rect1[0] - rect2[0])
    x_diff_top_left = abs((rect1[0] + rect1[2]) - (rect2[0] + rect2[2]))    
    
    if x_diff_top_right / float(scale_benchmark) > .05 or x_diff_top_left / float(scale_benchmark) > .05: 
        return False
    
    # largest rectangle absorbs the smaller
    x_coords = [rect1[0], rect2[0]]
    y_coords = [rect1[1], rect2[1]]
    widths = [rect1[2], rect2[2]]
    max_y_pos = max([rect1[1] + rect1[3], rect2[1] + rect2[3]])    
    
    combined_rect = (min(x_coords), min(y_coords), max(widths), max_y_pos - min(y_coords))
    
    return combined_rect
    
def check_rect_height(rect, height_threshold = 123):
    """
    Takes a rectangle and height threshold
    Returns true if area within acceptable range
    """
    
    assert type(rect) is tuple, "Rectangle must be a tuple"
    assert len(rect) == 4, "Rectangle is not in the required format (x, y, w, h)"
    
    height = rect[3]
    if .95 <= float(height) / height_threshold <= 1.05:
        return True
    else:
        return False

# Load the input file
cwd = os.getcwd().replace("\\", "/")
clf = joblib.load(cwd + "/data/digits_cls.pkl")

# Read input image
im = cv2.imread(cwd + "/data/errors_test/24_p.png")
im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
im_inverted = cv2.bitwise_not(im_gray)

# Get contours of image
src, ctrs, hier = cv2.findContours(im_inverted.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Draw rectangles around contour regions
rects = [cv2.boundingRect(ctr) for ctr in ctrs]

def process_rects(rects):
    """
    Consolidates vertically aligned rectangles
    Removes rectangles with non-relevant dimensions
    """
    if len(rects) == 0:
        return None
    
    # Consolidating vertically aligned rectangles
    indexes_to_remove = set([])
    to_add = []
    for index_1 in range(len(rects)):
        for index_2 in range(index_1 + 1, len(rects), 1):
            
            combined_rect = absorb_rect_below(rects[index_1], rects[index_2])
            if combined_rect:
                indexes_to_remove.add(index_1); indexes_to_remove.add(index_2)
                to_add.append(combined_rect)
    
    rects = [rect for index, rect in enumerate(rects) if index not in indexes_to_remove]
    rects.extend(to_add)
    
    # remove rectangles too small to be digits
    rects = [rect for rect in rects if check_rect_height(rect, height_threshold = 123)]
    
    # order from left to right
    rects.sort()    
    
    return rects

#rects = process_rects(rects)
def generate_digit_string(rects, image):
    digits = []
    for rect in rects:
      
        # resize rectangles to squares
        bounding_box = image[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]
        bounding_box = cv2.resize(bounding_box, (28,28), interpolation = cv2.INTER_AREA)
        bounding_box = cv2.dilate(bounding_box, (3,3))
        
        # extract hod features from bounding box
        roi_hog_fd = hog(bounding_box, orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1), visualise=False)
        nbr = clf.predict(np.array([roi_hog_fd], 'float64'))
        
        digits.append(nbr[0])
    
    return digits
    
# draw the rectangles    
#cv2.rectangle(im_inverted, (rect[0], rect[1]), 
#          (rect[0] + rect[2], rect[1] + rect[3]), 
#          70, 3)
#show_image(im_inverted)