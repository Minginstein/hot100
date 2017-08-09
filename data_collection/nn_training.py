# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 11:14:56 2016

NN Training Script

@author: David Roberts
"""

# core libraries
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Convolution2D, MaxPooling2D, Flatten
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
    given matrix of flattented pixel vectors, resizes 
    """
    
    new_shape = (int(ORIGINAL_SIZE[0]*scaling_factor), int(ORIGINAL_SIZE[1]*scaling_factor))
    new_size = new_shape[0]*new_shape[1]
    new_matrix = np.empty((0, new_size), dtype = np.uint8)
    
    for i in range(flattened_image_matrix.shape[0]):
        row = flattened_image_matrix[i].astype(np.uint8)
        image = row.reshape(ORIGINAL_SIZE)  # note this should be parameterized by a master variable script
        new_image = cv2.resize(image, new_shape[::-1])
        new_flattened_row = new_image.reshape((1, new_size))
        new_matrix = np.append(new_matrix, new_flattened_row, axis = 0)
        
    return new_matrix
      
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
    
def CNN_model_basic(num_classes, image_shape):
    """
    Constructs a 6 layer convolutional neural network with the following layers:
        1. Convolution layer - 32 filters (feature maps) convolve over pixel map, generating similarity "scores" for each pixel.
             - Results in a matrix of scores with the same size as the image
        2. Pooling layer which essentially scales this similiarty scores matrix down to half the size
        3. Dropout - regularization layer which randomly drops specified proporiton of neurons
        4. Flatten - flattens arrays out to be processed by standard layers
        5. Dense - standard, fully connected hidden layer
        6. Dense - 10 class output layer
    """
    
    # create model
    model = Sequential()
    model.add(Convolution2D(32, 5, 5, border_mode='valid', input_shape=(1, image_shape[0], image_shape[1]), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.1))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dense(num_classes, activation='softmax'))
	# Compile model
    model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
    
    return model
    
# initializing random seed to ensure reproducability
np.random.seed(10)

#%%
# loading data, transforming to desirable format
dataset = load_data()
dataset['image'] = rescale_images(dataset['image'], scaling_factor = .3)
IMAGE_SHAPE = (45, 28)

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
"""
Training a baseline model
"""

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
   at 30% 
Baseline Error: .12%
"""

"""
Larger image sizes resulted in worse accuracy, this makes sense to some degree.
Since we're looking simply at pixel values as opposed to hog features or contours, larger sizes just grant more chance that two pixels would not overlap
The shrinking process essentially maps surrounding pixels to one value, boiling more complex patterns down to simpler contours.  
"""

#%%
"""
Training a basic convolutional model
"""

X_train_CNN = X_train.reshape(X_train.shape[0], 1, IMAGE_SHAPE[0], IMAGE_SHAPE[1]).astype('float32')
X_val_CNN = X_val.reshape(X_val.shape[0], 1, IMAGE_SHAPE[0], IMAGE_SHAPE[1]).astype('float32')

CNN_basic = CNN_model_basic(10, IMAGE_SHAPE)
CNN_basic.fit(X_train_CNN, y_train, validation_data = (X_val_CNN, y_val), nb_epoch = 5, batch_size = 200, verbose = 2)

#%%
scores = CNN_basic.evaluate(X_val_CNN, y_val, verbose=0)
print("Baseline Error: %.2f%%" % (100-scores[1]*100))

# Baseline Error: 0.19%

"""
Seems to me that the error could likely be chalked up to labeling errors on my part
The regularization probably caused a decreases in accuracy over the basic model.
"""
#%% Saving the models
import os
CWD = os.getcwd().replace("\\", "/")
model.save(CWD + "/models/basic_NN.h5")
CNN_basic.save(CWD + "/models/CNN.h5")
