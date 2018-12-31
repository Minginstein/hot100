# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 12:35:50 2016

Training GUI - Object Oriented Approach

@author: David Roberts
"""

import tkinter as tk
from PIL import ImageTk, Image
import pandas as pd
import numpy as np
import os
from collections import deque


# Core Classes
class TrainingGUI(tk.Frame):
    """
    Takes as input a root window and an initialized "Train" Object
    Interacts with Train object to control ocr verification of images and save results
    """
    
    def __init__(self, parent, train_object, *args, **kwargs):
        """
        Initializes window, waits for user input   
        """
        self.parent = parent

        self.image_frame = tk.Frame(self.parent)
        self.bottom_frame = tk.Frame(self.parent)
        
        self.train = train_object
        next_forward = lambda event: self.next_image()
        self.parent.bind("<Return>", next_forward)
        
        # pack the frames
        self.image_frame.pack(side = tk.TOP)
        self.bottom_frame.pack(side = tk.BOTTOM)
        
        tk_compatible_img = ImageTk.PhotoImage(image = self.train.current_img)
        self.main_image = tk.Label(self.image_frame, image = tk_compatible_img)
        self.main_image.image = tk_compatible_img
        self.main_image.grid(row=0, column = 0)
        
        self.input_label = tk.Label(self.bottom_frame, text = "Input Correct Figure: ")
        self.input_label.grid(row = 0, column = 3)
        self.input_label.config(font = ("Courier", 30))
        
        self.entry_box = tk.Entry(self.bottom_frame, bg = 'black', fg='white', 
                                  font = ("Courier", 30), justify = tk.RIGHT, 
                                  insertbackground = 'white')
        self.entry_box.grid(row = 0, column = 4)
        self.entry_box.insert(0, self.train.current_stat)  
        
        self.save_button = tk.Button(master = self.bottom_frame, text = "SAVE", font = ("Courier", 30), command = self.save_work)
        self.save_button.grid(row = 0, column = 0)
        
        back_cmd = lambda : self.next_image(direction = "BACKWARD")
        self.back_button = tk.Button(master = self.bottom_frame, text = "BACK", font = ("Courier", 30), command = back_cmd)
        self.back_button.grid(row = 0, column = 1)
                
    def next_image(self, direction = "FORWARD"):
        """
        When enter is pressed, saves the user input to Train object, queries for next image to check
        """
        
        if direction == "FORWARD":
            # save inputted text
            input_text = int(self.entry_box.get())
            self.train.df.loc[self.train.current_img_id, 'correct_label'] = input_text
            
            # rotate the queue
            self.train.rotate_queue_left()
        
        elif direction == "BACKWARD":
            self.train.rotate_queue_right()
        
        image_row = self.train.df.loc[self.train.current_img_id]
        
        self.train.get_image(image_row.name)
        self.train.get_monthly_listeners(image_row.name)
        tk_compatible_img = ImageTk.PhotoImage(image=self.train.current_img)
        self.main_image.configure(image = tk_compatible_img)
        self.main_image.image = tk_compatible_img
        
        # clear input, give next values
        self.entry_box.delete(0, tk.END)
        self.entry_box.insert(0, self.train.current_stat)
        self.entry_box.icursor(0)
        
    def save_work(self):
        """
        When save button is pressed, saves Train.df to csv file
        """
        self.train.save_csv()


class Train():
    """
    Class for generating training examples and verifying/correcting Tesseract generated labels
    """

    def __init__(self, csv_file_path, png_dir):
        self.TARGET_CSV = csv_file_path
        self.PNG_DIR = png_dir
        self.current_img = None
        self.current_img_id = None
        self.df = None

    def import_csv(self):
        self.df = pd.read_csv(self.TARGET_CSV,
                              encoding='UTF-8',
                              )
        self.df.set_index(['artist_id'], inplace=True)

    def import_image_names(self):
        self.image_names = [name for name in os.listdir(self.PNG_DIR) if ".png" in name]

    def get_image(self, img_id, mode="PIL"):
        """
        Loads image given img_id in either PIL or cv2 format
        """
        assert type(img_id) is str, "image_id must be a string"

        self.current_img_id = img_id

        if mode == "PIL":
            self.current_img = Image.open(self.PNG_DIR + img_id + ".png")
        # elif mode == "OpenCV" or "opencv":
        #     img = cv2.imread(self.PNG_DIR + img_id + ".png", cv2.IMREAD_GRAYSCALE)
        #     self.current_img = img

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

    def get_correct_label(self, img_id):
        assert type(img_id) is str, "image_id must be a string"
        assert self.df is not None, "dataframe not yet initialized"

        val = self.df.loc[img_id, 'correct_label']

        if not np.isnan(val):
            self.current_label = int(val)
        elif np.isnan(val):
            self.current_label = ""

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


if __name__ == '__main__':

    # PROGRAM CONSTANTS
    CWD = ''
    TARGET_CSV = CWD + "/data/NN_training_examples/tesseract_classifications.csv"
    PNG_DIR = CWD + "/data/NN_training_examples/processed_imgs/"

    # Start labeling
    t = Train(TARGET_CSV, PNG_DIR)
    t.import_csv()
    t.initialize_training_queue()
    t.get_image(t.current_img_id)
    t.get_monthly_listeners(t.current_img_id)
                    
    root = tk.Tk()
    my_gui = TrainingGUI(root, t)
    root.mainloop()
