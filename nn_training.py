# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 11:14:56 2016

NN Training Script

@author: David Roberts
"""

# core libraries
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.utils import np_utils

# I/O operations
import pickle
import os

# image manipulation
import cv2

# load data from pickel file
CWD = os.getcwd().replace("\\", "/")
ORIGINAL_SIZE = (150,95)

def load_data(file_name = CWD + "/data/NN_training_examples/digit_dictionary.pkl"):
    data_dictionary = pickle.load(open(file_name, mode = "rb"))
    return data_dictionary
    
def rescale_images(flattened_image_matrix, scaling_factor= .50):
    """
    given pictures digit training data, rescales the images to reduce memory burden later on
    """
    
    new_shape = (int(ORIGINAL_SIZE[0]*scaling_factor), int(ORIGINAL_SIZE[1]*scaling_factor))
    new_size = new_shape[0]*new_shape[1]
    new_array = np.empty((0, new_size), dtype = np.uint8)
    
    for i in range(flattened_image_matrix.shape[0]):
        row = flattened_image_matrix[i].astype(np.uint8)
        image = row.reshape(ORIGINAL_SIZE)  # note this should be parameterized by a master variable script
        new_image = cv2.resize(image, new_shape[::-1])
        new_flattened_row = new_image.reshape((1, new_size))
        new_array = np.append(new_array, new_flattened_row, axis = 0)
        
    return new_array
      
# defining a simple CNN with only one hidden layer as baseline
def baseline_model(num_pixels, num_classes):
    # Construct 3 layer sequential model
    model = Sequential()
    
    # all layers are "dense", that is to say, all input values are connected to all subsequent activations
    model.add(Dense(num_pixels, input_dim = num_pixels, init = 'normal', activation = 'relu'))
    model.add(Dense(num_classes, input_dim = num_pixels, init = 'normal', activation = 'softmax'))
    
    # compile the model - train using Adam gradient descent method
    model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
    return model

# initializing random seed to ensure reproducability
np.random.seed(10)

# loading data, transforming to desirable format
dataset = load_data()
dataset['image'] = rescale_images(dataset['image'], scaling_factor = .3)

#%%
dataset['image'] = dataset['image'] / 255
dataset['label'] = dataset['label'].astype(np.int)
dataset['label'] = np_utils.to_categorical(dataset['label'])

#%%
sep = (dataset['label'].shape[0] // 5) * 4
X_train = dataset['image'][0:sep]
X_val = dataset['image'][sep:]
y_train = dataset['label'][0:sep]
y_val = dataset['label'][sep:]
num_pixels = dataset['image'].shape[1]

#%%
model = baseline_model(num_pixels, 10)
model.fit(X_train, y_train, validation_data = (X_val, y_val), nb_epoch = 5, batch_size = 200, verbose = 2)

# 8:37 start time, 8:41 finish\
scores = model.evaluate(X_val, y_val, verbose=0)
print("Baseline Error: %.2f%%" % (100-scores[1]*100))
"""
Scaled at 50% 
Baseline Error: 72.14% -- fook lol
"""

"""
Scaled at 20%
Baseline Error: .19%
"""

"""
Scaled at 30% 
Baseline Error: .12%
"""

"""
Larger image sizes resulted in worse accuracy, this makes sense to some degree.
Since we're looking simply at pixel values as opposed to hog features or contours, larger sizes just grant more chance that two pixels would not overlap
The shrinking process essentially maps surrounding pixels to one value, boiling more complex patterns down to simpler contours.  
"""

#==============================================================================
# #%%
# dataset_2 = load_data()
# 
# def show_digit(img, label):
#     reshaped = img.reshape((150, 95))
#     cv2.imshow("IMAGE LABEL" + str(label), reshaped)
#     cv2.waitKey(0)
#     
# for i in range(15):
#     img = dataset_2['image'][i].astype(np.uint8)
#     label = dataset_2['label'][i]
#     print(label)
#     show_digit(img, label)
#     
#==============================================================================
