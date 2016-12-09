# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 10:18:34 2016

Convert images to numpy array dataset 

@author: David Roberts
"""

# library imports
import os 
import numpy as np
import pandas as pd
import cv2
import PIL

# local imports
from open_cv_classify import generate_rects, process_rects, show_image
from training_gui_backend import Train

# constants
#CWD = os.getcwd().replace("\\", "/")
#TARGET_CSV = CWD + "/data/NN_training_examples/tesseract_classifications.csv"
#PNG_DIR = CWD + "/data/NN_training_examples/processed_imgs/"
DIGIT_IMAGE_SHAPE = (150,95)   # all images of individual digits will be reformatted to this size
DIGIT_IMAGE_SIZE = 150*95

def import_labeled_data():
    """
    Initializes Train object with df consisting of only labeled data
    """
    
    t = Train()
    t.import_csv()
    t.df.dropna(subset = ['correct_label'], inplace = True)
                
    return t
    
def process_cv2_image(img):
    assert type(img).__module__ == np.__name__, "Image must be represented as numpy array"
    
    # convert to black_background
    img = cv2.bitwise_not(img)
    
    bounding_boxes = generate_rects(img)
    bounding_boxes = process_rects(bounding_boxes)
    
    return bounding_boxes
    
    
def reshape_image(img, shape = DIGIT_IMAGE_SHAPE):
    """
    Takes a black and white image represented as numpy array, must be smaller than shape tuple
    Adds white in equal porportion around image until conforms with given shape tuple
    Returns PIL image of correct shape
    """
    assert img.shape <= shape, "provided image cannot be larger than provided shape"
    
    img = PIL.Image.fromarray(img)
    img_w, img_h = img.size
    background = PIL.Image.new('L', shape[::-1], (255))
    bg_w, bg_h = background.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img, offset)
    
    array = np.asarray(background)
    row = array.reshape(1, array.size)
    return row

def gen_digits_training_data():
    """
    Iterates through all labeled examples, separating digits, and saving them as row vectors in master datafile
    Saves data file
    """
    
    t = import_labeled_data()
    
    single_digits_arr = []
    for number in np.asarray(t.df['correct_label'].iloc[0:20]):
        single_digits_arr.extend(list(str(int(number))))
        

    
    dataset = {'INFO': "BLAH BLAH BLAH", 
                'labels': np.asarray(single_digits_arr),
                'images': np.empty((0, DIGIT_IMAGE_SIZE), dtype = np.int32)}
                
    for index, row in t.df.iloc[0:20].iterrows():
        t.get_image(index, mode = 'open_cv')
        rects = process_cv2_image(t.current_img)
        digits = [t.current_img[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]] for rect in rects]
        
        for digit in digits:
            row_vector = reshape_image(digit)
            dataset['images'] = np.append(dataset['images'], row_vector, axis=0)
            
#    assert len(dataset['labels']) == len(dataset['images']), "dataset must have one label for each row"
        
    return dataset
        
        
        

    
    
    


#==============================================================================
# from PIL import Image
# img = Image.open('/pathto/file', 'r')
# img_w, img_h = img.size
# background = Image.new('RGBA', (1440, 900), (255, 255, 255, 255))
# bg_w, bg_h = background.size
# offset = ((bg_w - img_w) / 2, (bg_h - img_h) / 2)
# background.paste(img, offset)
# background.save('out.png')
#     
#     
#==============================================================================
    
    
    

def show_rects(image, rects):
    for rect in rects:
        cv2.rectangle(image, (rect[0], rect[1]), 
              (rect[0] + rect[2], rect[1] + rect[3]), 
              70, 3)

    cv2.imshow("digit", image)
    cv2.waitKey()


#%%
t = Train()
t.import_csv()
t.get_image(t.df.iloc[0].name, mode = "opencv")
im = t.current_img

#%%

rects = process_cv2_image(im)
rect = rects[0]

digits = [im[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]] for rect in rects]

#for digit in digits:
#    show_image(digit)

im2 = cv2.imread(os.getcwd().replace("\\", "/") + "/data/errors_test/24_p.png")
im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

rects0 = process_cv2_image(im2)
