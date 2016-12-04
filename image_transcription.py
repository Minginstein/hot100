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
        
    def __str__(self):
        pass
        
    def transcribe_image(self):
        """
        Opens image, uses digit recognition to return int monthly_listeners value
        """
        string = ts.image_to_string(self.processed_img, config = "--psm 7 digits")
        self.monthly_listeners = string

    def prepare_image(self):
        """
        Crops and resizes the image. Inverts colors and applies high contrast
        """
        # crop the image
        temp = self.original_img
        width, height = temp.size
        temp = temp.crop((70, 0, width, height - 5))
        
        # scale the image up
        size = temp.size
        new_size = (size[0]*10, size[1]*10)
        temp = temp.resize(new_size, Image.ANTIALIAS)
        
        # apply transformations to improve transcription accuracy
        temp = temp.filter(ImageFilter.SHARPEN)
        temp = temp.convert('L')
        temp = ImageOps.invert(temp)
        contrast = ImageEnhance.Contrast(temp)
        self.processed_img = contrast.enhance(3)
        
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
    
    for index, file in enumerate(target_images[0:30]):
        try:
            img = Image.open(target_dir + file)
            t = Transcriber(img, file)
            t.prepare_image()
            t.transcribe_image()
            t.monthly_listeners = int(t.monthly_listeners.replace(" ", ""))
            dataframe['monthly_listeners'][index] = t.monthly_listeners
            
        except Exception as e:
            print(e)
            
    dataframe.to_csv(cwd + "/data/monthly_listeners.csv")
            
main()        