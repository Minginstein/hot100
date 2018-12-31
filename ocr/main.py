# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 16:09:59 2016

Generate Monthly Listeners data

@author: David Roberts
"""

"""
SKETCH:
    1. cycles through all images in monthly_listeners folder, generating processed versions
    2. program image class with methods to return classified text from image
    3. cycle through all images, generating csv
"""

from transcribe import Transcriber, import_image_names
from keras.models import load_model
from PIL import Image
import os


TARGET_DATE = "2016-11-27"
CWD = os.getcwd().replace("\\", "/")
TARGET_DIR = CWD + "/data/monthly_listeners/" + TARGET_DATE + "/"
PROCESSED_DIR = CWD + "/data/monthly_listeners/" + TARGET_DATE + "_processed/"

model = load_model(CWD + "/models/basic_NN.h5")


os.mkdir(PROCESSED_DIR)

target_images = import_image_names(TARGET_DIR)
for index, file in enumerate(target_images):        
        img = Image.open(TARGET_DIR + file)
        t = Transcriber(img, file)
        t.prepare_image()
        t.processed_img.save(PROCESSED_DIR + file)
