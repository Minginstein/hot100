# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 15:24:51 2016

@author: David
"""

import cv2
import numpy as np

def show_rects(image, rects):
    for rect in rects:
        cv2.rectangle(image, (rect[0], rect[1]), 
              (rect[0] + rect[2], rect[1] + rect[3]), 
              70, 3)

    cv2.imshow("digit", image)
    cv2.waitKey()

def show_image(img):
    """
    Takes a cv2 image as numpy array, displays it with infinite waitkey
    """
    cv2.imshow("Image", img)
    cv2.waitKey()
    
def process_cv2_image(img):
    assert type(img).__module__ == np.__name__, "Image must be represented as numpy array"
    
    # convert to black_background
    
    inverted_copy = invert_colors(img)
    bounding_boxes = generate_rects(inverted_copy)
    bounding_boxes = process_rects(bounding_boxes)
    
    return bounding_boxes
    
def invert_colors(img):
    copy = img.copy()
    return cv2.bitwise_not(copy)
    
def generate_rects(img):
    """
    Takes a cv2.image object, generates bounding rectangles for major contours
    Returns list of rectangels formatted as tuple x, y, w, h
    """
    assert type(img).__module__ == np.__name__, "Image must be formatted as numpy array"

    # Get contours of image
    src, ctrs, hier = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes = [cv2.boundingRect(ctr) for ctr in ctrs]
    return bounding_boxes
    
def absorb_rect_below(rect1, rect2):
    """
    Given a set of rectangle tuples, combines rectangles that are in veritical alignment
    Rectangle tuples take the form x, y, w, h
    """
    
    combined_rect = (0,0,0,0)
    
    # establish that the lateral distances are similar
    ratio = float(rect1[2]) / rect2[2]
    scale_benchmark = max(rect1[2], rect2[2])

    if not .50 <= ratio <= 1.50:
        return False
       
    # establish that the rectangles are vertically aligned
    x_diff_top_right = abs(min(rect1[0] - rect2[0], rect2[0] - rect1[0]))
    x_diff_top_left = abs(min((rect1[0] + rect1[2]) - (rect2[0] + rect2[2]), (rect2[0] + rect2[2]) - (rect1[0] + rect1[2])))    
    
    if x_diff_top_right / float(scale_benchmark) > .30 or x_diff_top_left / float(scale_benchmark) > .30: 
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
    if .90 <= float(height) / height_threshold <= 1.10:
        return True
    else:
        return False

def process_rects(rects):
    """
    Consolidates vertically aligned rectangles
    Removes rectangles with non-relevant dimensions
    
    ERROR analysis:
    This does not update the rects throughout the process, could lead to errors if three rects are being combined
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

#==============================================================================
# #rects = process_rects(rects)
# def generate_digit_string_DEPRECATED(rects, image):
#     digits = []
#     for rect in rects:
#       
#         # resize rectangles to squares
#         bounding_box = image[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]
#         bounding_box = cv2.resize(bounding_box, (28,28), interpolation = cv2.INTER_AREA)
#         bounding_box = cv2.dilate(bounding_box, (3,3))
#         
#         # extract hod features from bounding box
#         roi_hog_fd = hog(bounding_box, orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1), visualise=False)
#         nbr = clf.predict(np.array([roi_hog_fd], 'float64'))
#         
#         digits.append(nbr[0])
#     
#     return digits
#==============================================================================