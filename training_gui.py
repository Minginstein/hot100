# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 12:35:50 2016

Training GUI - Object Oriented Approach

@author: David Roberts
"""

"""
Created on Wed Dec  7 20:15:38 2016

Training GUI

@author: David Roberts
"""

import tkinter as tk
from training_gui_backend import *
import random

class TrainingGUI(tk.Frame):
    """
    Takes as input a root window and an initialized "Train" Object
    Interacts with Train object to control label verification of images and save results
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

   
if __name__ == '__main__':  
    t = Train()
    t.import_csv()
    t.initialize_training_queue()
    t.get_image(t.current_img_id)
    t.get_monthly_listeners(t.current_img_id)
                    
    root = tk.Tk()
    my_gui = TrainingGUI(root, t)
    root.mainloop()       