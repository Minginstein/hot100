"""
SQLAlchemy based functions used for database creation and data collection.

Currently using SQLite dialect, but SQLAlchemy will allow simple scaling if it becomes unwieldy.
"""


from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date, Float, Boolean,\
    create_engine
import os


def create_db(db_engine, overwrite=False):
    """Initializes database with all necessary tables.

    Parameters
        db_engine : SqlAlchemy Database Engine
        overwrite : Boolean indicating whether or not to overwrite the database

    Returns
        None
    """
    metadata = MetaData()
    artists = Table('Artist', metadata,
        Column('SpotArtistID', String),
        Column('OnSpotify', Boolean),
        Column('BillBoardName', String),
        Column('SpotifyName', String),
        Column('Genres', String)
    )

    artist_spot_fact_table = Table('ArtistSpotifyFact', metadata,
        Column('ArtistID', String, ForeignKey("Artist.ArtistID"), nullable=False),
        Column('Date', Date, nullable=False),
        Column('Popularity', Integer),
        Column('Followers', Integer),
        Column('MonthlyListeners', Integer)
    )

    billboard_position = Table('BillBoardTrackPosition', metadata,
        Column('ChartReleaseDate', Date, nullable=False),
        Column('Position', Integer),
        Column('TrackName', Integer),
        Column('ArtistName', Integer),
    )

    tracks = Table('Track', metadata,
        Column('TrackID', String, primary_key=True),
        Column('ArtistID', String, ForeignKey("Artist.SpotArtistID"), nullable=False),
        Column('TrackName', String),
        Column('Acousticness', Float),
        Column('Danceability', Float),
        Column('Energy', Float),
        Column('Instrumentalness', Float),
        Column('Key', Integer),
        Column('Liveness', Float),
        Column('Loudness', Float),
        Column('Mode', Integer),
        Column('Tempo', Integer),
        Column('TimeSignature', Integer),
        Column('Valence', Integer),
        Column('Speechiness', Integer),
    )

    tracks_fact_table = Table('TrackSpotifyFact', metadata,
        Column('TrackID', String, ForeignKey("Track.TrackID")),
        Column('Date', Date, nullable=False),
        Column('Popularity', Integer)
    )

    if db_engine.driver == 'pysqlite' and (overwrite or not os.path.exists('hot100.sqlite')):
        metadata.create_all(db_engine)
    else:
        raise(Exception, 'Target SQLite database exists')


if __name__ == '__main__':
    db_engine = create_engine('sqlite:///hot100.sqlite')
    create_db(db_engine)
