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
import numpy as np
import os
import traceback
import time

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

    
"""
SHOULD PICK UP TRACK AND ARTIST POPULARITY WHILE I'M AT IT
"""    

def get_artist_info(file_name, spotipy_client = None):
    """
    Takes a filename as string and an array of spotify track URI's
    Queries Spotify API for artist ids
    Returns dataframe with artist ID and popularity as well as track popularity
    """
    
    # Importing csv with track URI's
    cwd = os.getcwd()
    file_path = cwd + "\\data\\" + file_name
    
    # Initialize dataframe
    target_fields = ['track_id']
    track_id = pandas.Series(pandas.read_csv(file_path, index_col = False, usecols = target_fields)['track_id'])
    track_id = track_id.drop_duplicates()
    track_id = track_id.dropna()
    
    artist = []
    artist_id = []
    for i in range(0, len(track_id), 50):
        end_index = min(i+50, len(track_id))
        
        try:
            tracks = spotipy_client.tracks(track_id[i:min(i+50, end_index)])['tracks']
        except spotipy.SpotifyException:
            time.sleep(90)

        error_count = 0
        for track in tracks:
            try:
                artist.append(track['artists'][0]['name'])
                artist_id.append(track['artists'][0]['id'])
            except:
                traceback.print_last()
                artist.append(np.NaN)
                artist_id.append(np.NaN)
                error_count += 1
        
        print ("Track Group: ", i, ", Error Count: ", error_count)
        
    for i, a in enumerate(artist):
        artist[i] = a.encode('latin-1', 'ignore').decode('latin-1')
        
    assert len(artist) == len(artist_id), "Artist columns are not the same length"
    assert len(artist) == len(track_id), "Artist column is not the same length as track_id column"
      
    cross_ref_df = pandas.DataFrame(track_id)  
    artist = np.array(artist)
    artist_id = np.array(artist_id)
    
    cross_ref_df['artist'] = artist
    cross_ref_df['artist_id'] = artist_id
    
    return cross_ref_df
    

#%%
#==============================================================================
# 
# sp = authorize_spotify()
# df = get_artist_info('hot100_track_df.csv', spotipy_client = sp)
# df.to_csv(os.getcwd() + "\\data\\artist_info.csv", encoding = "latin-1")
#==============================================================================