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
from open_cv_classify import generate_rects, process_rects, process_cv2_image, show_image, show_rects
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
    
    dataset = {"INFO": {'source': 'Images extracted as part of hot100 from Spotify Desktop client', 'font': 'unknown :)', 'transformations': 'digits were extracted using contour analysis. They were then converted to grayscale, sharpened, inverted, contrasted to white/black and placed on a uniform white background', 'description': 'labels consists of 8024 digit labels. image array consists of 8024 rows representing 150 x 95 pixel images, flattened to fit in one row'}, 
                'label': [],
                'image': np.empty((0, DIGIT_IMAGE_SIZE), dtype = np.uint8)}
    
    errors = {'artist_id':[], 'label':[], 'rects':[]}
              
    int_index = 0
    for index, row in t.df.iterrows():
        print("Row {}".format(int_index))
        
        t.get_image(index, mode = 'open_cv')
        rects = process_cv2_image(t.current_img)
        digits = [t.current_img[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]] for rect in rects]
        
        label = list(str(int(row['correct_label'])))
        
        if len(rects) != len(label):
            errors['artist_id'].append(index)
        elif len(rects) == len(label):
            for digit in digits:
                row_vector = reshape_image(digit)
                dataset['image'] = np.append(dataset['image'], row_vector, axis=0)
            dataset['label'].extend(label)
        
        int_index += 1
    
    dataset['label'] = np.asarray(dataset['label'])
            
    assert len(dataset['label']) == len(dataset['image']), "dataset must have one label for each row"
    
   

    return dataset, errors

    
if __name__ == '__main__':
    data, errors = gen_digits_training_data()
    import pickle
    cwd = os.getcwd().replace("\\", "/")
    pickle.dump(data, open(cwd + "/data/NN_training_examples/digit_dictionary.pkl", mode = "wb"))
