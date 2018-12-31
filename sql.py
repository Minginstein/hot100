"""
SQLAlchemy based functions used for database creation and data collection.

Currently using SQLite dialect, but SQLAlchemy will allow simple scaling if it becomes unwieldy.
"""


from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date, Float, create_engine
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
        Column('ArtistID', String, primary_key=True),
        Column('Name', String),
        Column('Genres', String)
    )

    artist_spot_fact_table = Table('ArtistSpotifyFact', metadata,
        Column('ArtistID', String, ForeignKey("Artist.ArtistID"), nullable=False),
        Column('Date', Date, nullable=False),
        Column('Popularity', Integer),
        Column('Followers', Integer),
        Column('MonthlyListeners', Integer)
    )

    artist_bb_fact_table = Table('ArtistBillBoardFact', metadata,
        Column('ArtistID', String, ForeignKey("Artist.ArtistID"), nullable=False),
        Column('ChartReleaseDate', Date, nullable=False),
        Column('LastWeekPosition', Integer),
        Column('CurrentPosition', Integer),
        Column('PeakPosition', Integer),
        Column('WeeksOnChart', Integer)
    )

    tracks = Table('Track', metadata,
        Column('TrackID', String, primary_key=True),
        Column('ArtistID', String, ForeignKey("Artist.ArtistID"), nullable=False),
        Column('Name', String),
        Column('Acousticness', Float),
        Column('Danceability', Float),
        Column('Energy', Float),
        Column('Instrumentalness', Float),
        Column('Key', Integer),
        Column('Liveness', Float),
        Column('Loudness', Float),
        Column('Mode', Integer),
        Column('Tempo', Integer),
        Column('Time_signature', Integer),
        Column('Valence', Integer),
        Column('Speechiness', Integer),
    )

    tracks_fact_table = Table('TrackSpotifyFact', metadata,
        Column('TrackID', String, ForeignKey("Track.TrackID")),
        Column('Date', Date, nullable=False),
        Column('Popularity', Integer)
    )

    if db_engine.driver == 'pysqlite' and not os.path.exists('hot100.sqlite'):
        metadata.create_all(db_engine)


if __name__ == '__main__':
    db_engine = create_engine('sqlite:///hot100.sqlite')
    create_db(db_engine)
