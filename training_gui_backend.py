# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 11:18:42 2016

Functions for generating and labeling training data

@author: David Roberts
"""

"""
Design sketch

    1. takes csv with Tesseract monthly listeners 
    2. isolates digits using cv2
    3. incorporates GUI funcitonality to confirm the label or input new label
    4. standardizes the digit image size, saves to numpy array (same format as MNSIT)

"""

# library imports
import pandas as pd
import numpy as np
import os
from PIL import Image, ImageTk
from collections import deque

# constants
CWD = os.getcwd().replace("\\", "/")
TARGET_CSV = CWD + "/data/NN_training_examples/tesseract_classifications.csv"
PNG_DIR = CWD + "/data/NN_training_examples/processed_imgs/"

# core class
class Train():
    """
    Class for generating training examples and verifying/correcting Tesseract generated labels 
    """
    
    def __init__(self, csv_file_path = TARGET_CSV, png_dir = PNG_DIR):
        self.TARGET_CSV = csv_file_path
        self.PNG_DIR = png_dir
        self.current_img = None
        self.current_img_id = None
        self.df = None
     
    def import_csv(self):
        self.df = pd.read_csv(self.TARGET_CSV, 
                                        encoding = 'UTF-8', 
                                        )
        self.df.set_index(['artist_id'], inplace = True)
        
    def import_image_names(self):
        self.image_names =  [name for name in os.listdir(self.PNG_DIR) if ".png" in name]
        
    def get_image(self, img_id):
        assert type(img_id) is str, "image_id must be a string"

        self.current_img_id = img_id
        self.current_img = Image.open(self.PNG_DIR + img_id + ".png")
        
        if self.current_img is None:
            print(img_id + " was not loaded correctly")
            self.current_img = None
            self.current_img_id = None
        else:
            print(img_id + " was loaded successfully")
            
    def get_monthly_listeners(self, img_id):
        assert type(img_id) is str, "image_id must be a string"
        assert self.df is not None, "dataframe not yet initialized"
        
        val = self.df.loc[img_id, 'monthly_listeners']

        if not np.isnan(val):
            self.current_stat = int(val)
        elif np.isnan(val):
            self.current_stat = ""
            
    def initialize_training_queue(self):
        """
        Stores list dataframe rows without verified labels
        """
        assert self.df is not None, "dataframe not yet initialized"

        unverified_rows = self.df[np.isnan(self.df['correct_label'])].index
        self.q = deque(unverified_rows)
        self.current_img_id = self.q[0]
        self.first_id = self.q[0]
        
    def rotate_queue_left(self):
        """
        Pops next unverified index off the queue
        Adds last id to the cache to retrieve if needed
        """
        
        self.q.rotate(-1)
        self.current_img_id = self.q[0]
        
        if self.current_img_id == self.first_id:
            print("All labels have been verified!")
            self.save_csv()
            
    def rotate_queue_right(self):
        self.q.rotate(1)
        self.current_img_id = self.q[0]
                
    def save_csv(self):
        assert self.df is not None, "dataframe not yet initialized"
        self.df.to_csv(self.TARGET_CSV)   