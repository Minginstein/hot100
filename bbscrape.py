# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 15:37:06 2016

@author: David Roberts

Scraping Billboard Hot 100 Archives
http://www.billboard.com/archive/
"""

import requests
import bs4
import pandas
import numpy as np

class BillBoard():
    """
    Base class with methods for scraping and storing Hot 100 Archive data
    """
    
    def __init__(self):
        self.current_year = None
        self.track_dataframe_row = {"chart_date": [], "id": [], "track_name": [], "artist": [],"current_week_rank": [], "last_week_rank": [], "weeks_on_chart": [], "peak_rank": []}
        self.track_df = pandas.DataFrame(self.track_dataframe_row, columns = ['chart_date', 'id', 'track_name', 'artist', 'current_week_rank', 'last_week_rank', 'weeks_on_chart', 'peak_rank'])
        self.audio_features_df = None
        self.joined_df = None        
        
    def get_chart_dates(self, year):
        """
        Takes a year represented as string
        Navigates to Hot 100 archive for that year
        Generates a list with dates for weekly charts. 
        """
        response = requests.get("http://www.billboard.com/archive/charts/{}/hot-100".format(year))
        html = response.content
        
        soup = bs4.BeautifulSoup(html, "lxml")
        week_elements = soup.findAll("td", class_ = "views-field views-field-field-chart-date")
        dates = [week.a.get('href')[8:18] for week in week_elements]
        
        return dates
        
    def get_weekly_chart(self, date):
        """
        Takes a date
        Navigates to Hot 100 for that week
        Parses html to extract relevant data
        Concatenates resulting dataframe to end of Billboard track dataframe
        """
        
        url = "http://www.billboard.com/charts/hot-100/" + date
        response = requests.get(url)
        html = response.content
        
        soup = bs4.BeautifulSoup(html, "lxml")
        tracks = soup.findAll("article", class_ = "chart-row")
        
        # Initializing weekly track dataframe
        track_dataframe_row = {"chart_date": [], "id": [], 
                               "track_name": [], "artist": [],
                               "current_week_rank": [], "last_week_rank": [],
                               "weeks_on_chart": [], "peak_rank": []
                               }
        
        track_df = pandas.DataFrame(track_dataframe_row, columns = ['chart_date', 'id', 'track_name', 'artist', 'current_week_rank', 'last_week_rank', 'weeks_on_chart', 'peak_rank'])
        
        # Iterate through Hot 100 tracks, parsing table
        for track in tracks:
            row_dict = {}            
            
            row_dict['chart_date'] = [date]
            row_dict['id'] = [track.get('data-spotifyid')]  
            
            # Modfiy string for artist_name
            artist_string = track.h3
            
            if artist_string is None:
                artist_string = track.a                
            
            artist_string = artist_string.text
            artist_string = artist_string.replace("\n", "")
            artist_string_edited = artist_string.strip()
                        
            row_dict['artist'] = [artist_string_edited]
            row_dict['track_name'] = [track.h2.text]
            
            # Stat element
            span_elements = track.findAll('span')
            
            row_dict['current_week_rank'] = [span_elements[0].text]
            
            # If the song was previously on the charts
            if len(span_elements) == 8:   
                row_dict['last_week_rank'] = [span_elements[3].text]
                row_dict['weeks_on_chart'] = [span_elements[7].text]
                row_dict['peak_rank'] = [span_elements[5].text]
            else:
                row_dict['last_week_rank'] = [np.nan]
                row_dict['weeks_on_chart'] = [np.nan]
                row_dict['peak_rank'] = [np.nan]
            
            # Using np.nan to represent null values
            row_dict_copy = row_dict.copy()
            for key, value in row_dict_copy.items():
                if value[0] is None or value[0] == "--":
                    row_dict[key] = np.nan
                        
            temp_df = pandas.DataFrame(row_dict)
            track_df = pandas.concat([track_df, temp_df], ignore_index = True)
        
        return track_df
        
    def collect_all_lists(self, start_year, end_year):
        """
        Given a start year and an end year, collect all billboard 100 weekly lists
        Saves to Billboard object
        """
        
        for year in range(start_year, end_year + 1, 1):
            dates = self.get_chart_dates(str(year))
            
            for date in dates:
                print("Date: ", date)
                weekly_chart = self.get_weekly_chart(date)
                self.track_df = self.track_df.append(weekly_chart, ignore_index = True)
                
    def dedup_spotify_ids(self):
        """
        Drop all spotify ids to one column
        Remove duplicates
        Returns series of spotify_ids
        """
        
        # Generating series of Spotify ids, no duplicates
        spot_ids = self.track_df['id']
        spot_ids = spot_ids.drop_duplicates()
        spot_ids = spot_ids.dropna()
        
        return spot_ids
        
    def merge_dataframes(self):
        self.joined_df = pandas.merge(self.track_df, self.audio_features_df, how='left', on='id')     