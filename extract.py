"""
Functions dedicated to extraction of data from the following sources:
1. Billboard Hot 100 Archives - http://www.billboard.com/archive/
2. Spotify Web API
3. Spotify Web Player

ToDo:
    - Refactor BillBoard object, no need for pandas. Use futures processing if possible
    - Refactor Spotify collection scripts, insert to database
"""

import requests
import bs4
import pandas
import numpy as np
import spotipy
import os
import traceback
import time


class BillBoard:
    """
    Base class with methods for scraping and storing Hot 100 Archive data
    """
    
    def __init__(self):
        self.current_year = None
        self.track_dataframe_row = {"chart_date": [], "track_id": [], "track_name": [], "artist": [], "current_week_rank": [], "last_week_rank": [], "weeks_on_chart": [], "peak_rank": []}
        self.track_df = pandas.DataFrame(self.track_dataframe_row, columns = ['chart_date', 'track_id', 'track_name', 'artist', 'current_week_rank', 'last_week_rank', 'weeks_on_chart', 'peak_rank'])
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
        track_dataframe_row = {"chart_date": [], "track_id": [], 
                               "track_name": [], "artist": [],
                               "current_week_rank": [], "last_week_rank": [],
                               "weeks_on_chart": [], "peak_rank": []
                               }
        
        track_df = pandas.DataFrame(track_dataframe_row, columns = ['chart_date', 'track_id', 'track_name', 'artist', 'current_week_rank', 'last_week_rank', 'weeks_on_chart', 'peak_rank'])
        
        # Iterate through Hot 100 tracks, parsing table
        for track in tracks:
            row_dict = {}            
            
            row_dict['chart_date'] = [date]
            row_dict['track_id'] = [track.get('data-spotifyid')]  
            
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
        spot_ids = self.track_df['track_id']
        spot_ids = spot_ids.drop_duplicates()
        spot_ids = spot_ids.dropna()
        
        return spot_ids
        
    def merge_dataframes(self):
        self.joined_df = pandas.merge(self.track_df, self.audio_features_df, how='left', on='id')


def authorize_spotify():
    """
    Initializes Spotify API object
    Requires that a local server is running for callback
    Will prompt for manual input, copying URL from browser
    """

    token = spotipy.util.prompt_for_user_token(spot_keys['user'], \
                                               scope=None, \
                                               client_id=spot_keys['client_id'], \
                                               client_secret=spot_keys['client_secret'], \
                                               redirect_uri=spot_keys['redirect_uri'])

    sp = spotipy.Spotify(auth=token)

    return sp


def get_audio_features(spot_ids, spotipy_client=None):
    """
    Peels track_df down to a series of spotify ids with no duplicates
    Iterates through the series in chunks of 50, querying audio features
    """
    series_length = len(spot_ids)
    full_list = []

    for i in range(0, series_length, 50):
        print("Audio Features: ", i)
        result = spotipy_client.audio_features(spot_ids[i: i + 50])
        full_list = full_list + result

    audio_features_df = pandas.DataFrame(full_list)

    return audio_features_df


def get_artist_info(file_name, spotipy_client=None):
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
    track_id = pandas.Series(pandas.read_csv(file_path, index_col=False, usecols=target_fields)['track_id'])
    track_id = track_id.drop_duplicates()
    track_id = track_id.dropna()

    artist = []
    artist_id = []
    for i in range(0, len(track_id), 50):
        end_index = min(i + 50, len(track_id))

        try:
            tracks = spotipy_client.tracks(track_id[i:min(i + 50, end_index)])['tracks']
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

        print("Track Group: ", i, ", Error Count: ", error_count)

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


def scrape_playlists():
    """
    Takes a integer formatted year,
    Scrapes all hot 100 playlists until that year
    """

    # Billboard Scrape
    bb = BillBoard()
    bb.collect_all_lists(1958, 2018)
    bb.track_df.to_csv('hot100_track_df.csv')

    bb = BillBoard()
    print("initialized")
    bb.track_df = pandas.read_csv('hot100_track_df.csv', encoding="ISO-8859-1")

    # Spotify Query
    sp = authorize_spotify()
    bb.spot_ids = bb.dedup_spotify_ids()
    bb.audio_features_df = get_audio_features(bb.spot_ids, sp)
    bb.merge_dataframes()
    bb.joined_df.to_csv('hot100_full_df.csv')


if __name__ == "__main__":
    scrape_playlists()