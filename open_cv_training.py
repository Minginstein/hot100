# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 14:35:27 2016

OCR using OpenCV

@author: David
"""

# Module imports
from sklearn import datasets
from sklearn.externals import joblib
from skimage.feature import hog
from sklearn.svm import LinearSVC
import numpy as np

# Initializing Handwritten digit dataset
dataset = datasets.fetch_mldata("MNIST Original")


#%%
# Creating feature and lable sets
features = np.array(dataset.data, 'int16')
labels = np.array(dataset.target, 'int')

list_hog_fd = []
for feature in features:
    fd = hog(feature.reshape((28,28)), 
             orientations = 9, 
             pixels_per_cell= (14,14),
             cells_per_block=(1, 1), 
             visualise=False)
             
    list_hog_fd.append(fd)
hog_features = np.array(list_hog_fd, 'float64')

#%%

clf = LinearSVC()
clf.fit(hog_features, labels)

import os
cwd = os.getcwd().replace("\\", "/")
joblib.dump(clf, cwd + "/data/digits_cls.pkl", compress=3)
