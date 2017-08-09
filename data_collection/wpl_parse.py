# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 13:44:23 2017

@author: David Roberts
"""

from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np

# Constants
REPLACEMENT_DICT = {".mp3" : "", ".wav" : "", ".wma" : "", "- " : "", "&amp;" : "&", "&apos;" : "'", "Disc": ""}
COLUMNS = {"track_id": [], "search_term_list": [], "original_string": []}
TEST_FP = "./wpl/test_playlist.xml"

# Main functions 
def generate_dataframe(file_path, cols):
    
    # Gen empty dataframe
    df = pd.DataFrame(cols)
    
    # Open and read target file
    infile = open(file_path,"r") 
    contents = infile.read()
    soup = BeautifulSoup(contents,'xml')
    tracks = soup.find_all('media')
    
    # Iterate through tracks, add a row to dataframe
    for track in tracks:
        row = cols.copy()
        string = track.get('src')
        row['original_string'] = string
        row['search_term_list'] = edit_track_string(string)    
        row['track_id'] = None
        df = df.append(row, ignore_index = True)
    
    df.to_csv(file_path.replace(".xml", ".csv"))

    
# Helper funtcions
def edit_track_string(track_string):
    """
    Uses regex and string methods to remove unecessary elements of track strings 
    Returns list of strings
    """
    
    split = [replace_all(elem, REPLACEMENT_DICT)
                 for elem in track_string.split("\\") 
                     if ".." not in elem]
    
    return split
    
def replace_all(text, replacement_dict):
    
    for i, j in replacement_dict.items():
        text = text.replace(i, j)    
        
    text = re.sub("\[(.*?)\]|\((.*?)\)|[0-9]{0,2}[,.]|[0-9]{2}", "", text)
    text = text.strip()
    
    return text
    

# Testing
# generate_dataframe(TEST_FP, COLUMNS)