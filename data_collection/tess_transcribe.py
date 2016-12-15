# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 12:33:01 2016

Transcribe monthly listeners figure using py-tesseract

@author: David
"""

import pytesseract as ts
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import os
import pandas as pd
import numpy as np

def import_image_names(file_path):
    """
    Imports image file names from specified directory
    Returns list of all images
    """
    
    return [name for name in os.listdir(file_path) if ".png" in name]
 
class Transcriber():
    """
    Transcription class with methods to handle individual images
    """
    
    def __init__(self, img, file_name):
        self.artist_id = file_name[0:len(file_name) - 4]
        self.monthly_listeners = None
        self.original_img = img
        self.processed_img = None
        
    def transcribe_image(self):
        """
        Prepares image, uses digit recognition to return int monthly_listeners value
        """
        self.prepare_image(contrast_enhancement = 3, contrast_threshold = 85)
        string = ts.image_to_string(self.processed_img, config = "--psm 7 digits")

        digits = [letter for letter in string if letter.isdigit()]
        
        if len(digits) > 0:
            self.monthly_listeners = int("".join(digits))
        else: 
            self.monthly_listeners = np.NaN

    def prepare_image(self, contrast_enhancement = 3, contrast_threshold = 85):
        """
        Crops and resizes the image. Inverts colors and applies high contrast
        """
        # crop the image
        temp = self.original_img
        width, height = temp.size
        temp = temp.crop((70, 0, width, height - 5))
        
        # scale the image up
        size = temp.size
        new_size = (size[0]*15, size[1]*15)
        temp = temp.resize(new_size, Image.ANTIALIAS)
        
        # apply transformations to improve transcription accuracy
        temp = temp.filter(ImageFilter.SHARPEN)
        temp = temp.convert('L')
        temp = ImageOps.invert(temp)
        contrast = ImageEnhance.Contrast(temp)
        temp = contrast.enhance(contrast_enhancement)
        
        # turn all "non-black" pixels white
        pixel_map = np.asarray(temp)
        pixel_map.flags["WRITEABLE"] = True
        pixel_map[pixel_map > contrast_threshold] = 255
        
        # expand right margin
        rows, cols = pixel_map.shape
        all_white_array = np.full((rows, 50), 255, dtype = np.uint8)
        pixel_map_white_margin = np.concatenate((pixel_map, all_white_array), axis = 1)
        self.processed_img = Image.fromarray(pixel_map_white_margin)
        
def main():
    """
    Imports monthly listeners images
    Iterates through files, transcribing figure
    Saves output csv file to data directory
    """
    
    # Configuration    
    cwd = os.getcwd().replace("\\", "/")
    target_dir = cwd + "/data/test_images/"
    target_images = import_image_names(target_dir)
    
    ts.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'

    # Initialize dataframe
    dataframe = pd.DataFrame({'artist_ids': [file_name[0:len(file_name)-4] for file_name in target_images]})    
    dataframe['monthly_listeners'] = np.nan
    
    error_indices = []
    
    for index, file in enumerate(target_images):
        #if index not in [23,24,26]:continue
        
        try:
            img = Image.open(target_dir + file)
            t = Transcriber(img, file)
            t.transcribe_image()
            dataframe['monthly_listeners'][index] = t.monthly_listeners
            t.processed_img.save(cwd + "/data/NN_training_examples/processed_imgs/" + file)
            
        except Exception as e:
            error_indices.append((index, t.processed_img))
            t.original_img.save(cwd + "/data/errors_test/" + str(index) + "_o.png")
            t.processed_img.save(cwd + "/data/NN_training_examples/processed_imgs/errors/" + file)
            print(e)
            
    dataframe.to_csv(cwd + "/data/NN_training_examples/tesseract_classifications.csv")
    
    return error_indices