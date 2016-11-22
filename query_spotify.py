# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 11:40:57 2016

@author: David

Function for collecting audio features from Spotify Web API
"""

from spotify_keys import spot_keys   # Import your own set of spotify keys! 
import spotipy
from spotipy import util
import pandas

def authorize_spotify():
    """
    Initializes Spotify API object
    Requires that a local server is running for callback 
    Will prompt for manual input, copying URL from browser
    """
    
    token = spotipy.util.prompt_for_user_token(spot_keys['user'], \
                                scope= None, \
                                client_id= spot_keys['client_id'], \
                                client_secret= spot_keys['client_secret'], \
                                redirect_uri= spot_keys['redirect_uri'])
                                
    sp = spotipy.Spotify(auth=token)
    
    return sp

def get_audio_features(spot_ids, spotipy_client = None):
    """
    Peels track_df down to a series of spotify ids with no duplicates
    Iterates through the series in chunks of 50, querying audio features
    """
    series_length = len(spot_ids)
    full_list = []
    
    for i in range(0, series_length, 50):
        print ("Audio Features: ", i)
        result = spotipy_client.audio_features(spot_ids[i : i+50])
        full_list = full_list + result 
        
    audio_features_df = pandas.DataFrame(full_list)
    
    return audio_features_df