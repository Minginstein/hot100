# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 16:00:29 2016

Master
1. Collects all Billboard lists, saves to object.track_df
2. Queries Spotify for their audio features
"""

import pandas

import bbscrape
from query_spotify import authorize_spotify
from query_spotify import get_audio_features

def main():
    """
    Takes a integer formatted year, 
    Scrapes all hot 100 playlists until that year
    """
    
    # Billboard Scrape
#    bb = bbscrape.BillBoard()
#    bb.collect_all_lists(2016, 2016)
#    bb.track_df.to_csv('hot100_track_df.csv')
    
    bb = bbscrape.BillBoard()
    print("initialized")
    bb.track_df = pandas.read_csv('hot100_track_df_2016.csv', encoding = "ISO-8859-1")
    
    # Spotify Query
    sp = authorize_spotify()
    bb.spot_ids = bb.dedup_spotify_ids()
    bb.audio_features_df = get_audio_features(bb.spot_ids, sp)
    bb.merge_dataframes()
    bb.joined_df.to_csv('hot100_full_df.csv')

if __name__ == "__main__":
    main()