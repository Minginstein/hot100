"""
Functions dedicated to extraction of data from the following sources:
1. Billboard Hot 100 Archives - http://www.billboard.com/archive/
2. Spotify Web API
3. Spotify Web Player

ToDo:
    - Refactor Spotify collection scripts, insert to database
"""

import requests
import bs4
import pandas
import numpy as np
import spotipy
import os
import time


def get_weekly_chart_dates(self, year):
    """Return a list of weekly chart dates for the given year

    Parameters
    ----------
        year : str

    Returns
    -------
        list[str]
    """
    response = requests.get("http://www.billboard.com/archive/charts/{}/hot-100".format(year))
    week_elements = bs4.BeautifulSoup(response.content, "html-parser").findAll("td")

    # Example: <td><a href="/charts/hot-100/1959-02-16">February 16</a></td>,
    date_list = [week.a.get('href')[8:18] for week in week_elements]
    return date_list


def get_weekly_chart(self, date):
    """Returns Billboard chart as a list of dictionaries.

    Dict Example: {
         'Position': int,
         'TrackName: str,
         'ArtistName: str
    }

    Parameters
    ----------
        date : str

    Returns
    -------
        list[dict]
    """

    url = "http://www.billboard.com/charts/hot-100/" + str(date)
    response = requests.get(url)
    html = response.content
    soup = bs4.BeautifulSoup(html, "html.parser")

    # extract the top track
    top_track_dict = dict({})
    top_track_dict['ArtistName'] = soup.find('div', {'class': 'chart-number-one__artist'}).a.contents[0].replace('\n', '')
    top_track_dict['TrackName'] = soup.find('div', {'class': 'chart-number-one__title'}).contents[0].replace('\n', '')
    top_track_dict['Position'] = 1

    # extract remaining tracks
    track_list = [top_track_dict]
    mapping_dict = {
        'data-rank': 'Position',
        'data-artist': 'ArtistName',
        'data-title': 'TrackName'
    }
    top_99_tracks = soup.findAll('div', {'class': 'chart-list-item'})
    for track in top_99_tracks:
        track_dict = {
            mapping_dict[key]: value.replace('\n', '')
            for key, value in track.attrs.items() if key in mapping_dict.keys()
        }
        track_dict['Position'] = int(track_dict['Position'])
        track_list.append(track_dict)

    assert len(track_list) == 100, 'There must be 100 tracks per Hot 100 list'
    return track_list
        

def collect_all_lists(start_year, end_year, db):
    """Insert all Hot 100 lists between provided years into target database

    Parameters
    ----------
        start_year : int
        end_year : int
        db : SQLAlchemy database engine

    Returns
    -------
    None
    """
    for year in range(start_year, end_year + 1, 1):
        dates = get_weekly_chart_dates(year)
        for date in dates:
            print("Date: ", date)
            weekly_chart = get_weekly_chart(date)


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
    bb = BillBoardScraper()
    bb.collect_all_lists(1958, 2018)
    bb.track_df.to_csv('hot100_track_df.csv')

    bb = BillBoardScraper()
    print("initialized")
    bb.track_df = pandas.read_csv('hot100_track_df.csv', encoding="ISO-8859-1")

    # Spotify Query
    sp = authorize_spotify()
    bb.spot_ids = bb.dedup_spotify_ids()
    bb.audio_features_df = get_audio_features(bb.spot_ids, sp)
    bb.merge_dataframes()
    bb.joined_df.to_csv('hot100_full_df.csv')


if __name__ == "__main__":
    # scrape_playlists()
    bb = BillBoardScraper()
    track_list = bb.get_weekly_chart('1959-02-16')
    print(track_list)