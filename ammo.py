"""Generates a Spotify playlist containing your top 50 songs of the past month.

Usage:
    python ../ammo.py

Outline:
    This script retrieves the necessary information required to create a Spotify
    playlist, such as a user's data, the playlist date, and its subsequent name.
    After asserting that a playlist with the chosen name does not already exist,
    one is generated with the user's most played songs from the previous month.

References:
    See https://developer.spotify.com/documentation/web-api/ for API info.
"""

# Built-In Libraries
from datetime import date
import os
import sys

# External Libraries
from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError
import spotipy
from spotipy import SpotifyOAuth


def abort_script(error_message='An error has occurred!'):
    """Exit the script after displaying an error message.

    Args:
        error_message: A string describing the error that has occurred.
    """

    # Provide the reason for the script being aborted.
    error_message = error_message + ' Script aborted.\n\n'
    sys.exit(error_message)


def set_environment_variables():
    """Set environment variables required for the Spotipy library."""
    
    # All the required Spotipy environment variables.
    environment_variables = {
        "SPOTIPY_CLIENT_ID": "Client ID: ",
        "SPOTIPY_CLIENT_SECRET": "Client Secret: ",
        "SPOTIPY_REDIRECT_URI": "Redirect URI: "
    }
    
    # Ensure all the Spotipy environment variables are set.
    missing_variables = [variable for variable,
                         prompt in environment_variables.items()
                         if not os.environ.get(variable)]
    if missing_variables:
        print('Please input the required items below.\n')
    
    # Set any missing Spotipy environment variables.
    for variable, prompt in environment_variables.items():
        if not os.environ.get(variable):
            os.environ[variable] = input(prompt)

    # For better script spacing.
    if missing_variables:
        print()


def get_spotify_data():
    """Authenticate a user's Spotify credentials to allow data requests.
    
    Returns:
        spotify_data: A Spotify object containing a user's Spotify data.
    """

    # Provide the required authentication scopes for requesting Spotify data.
    auth_manager = SpotifyOAuth(scope='user-top-read playlist-modify-public')
    spotify_data = spotipy.Spotify(auth_manager=auth_manager)

    return spotify_data


def generate_playlist_date(todays_date=None):
    """Generate the date of the playlist being created.

    Args:
        todays_date: The date that the function is being run on.

    Returns:
        playlist_date: The date of the playlist being created.
    """

    # Determine the current date.
    if not todays_date:
        todays_date = date.today()
    month = todays_date.month
    year = todays_date.year

    # Use the above to calculate the playlist's start date and name.
    if month == 1:
        playlist_date = todays_date.replace(year=year-1, month=12)
    else:
        playlist_date = todays_date.replace(month=month-1)

    return playlist_date


def generate_playlist_name(playlist_date=None, month_format='short'):
    """Generate the name of a playlist based on the date supplied.

    Args:
        playlist_date: The date of the playlist being created.
        month_format: A string that chooses how to display the month.

    Returns:
        A string representing the name of the playlist.
    """

    # Catch the case where no playlist date is supplied.
    if not playlist_date:
        abort_script(error_message='No playlist date supplied!')

    # Choose which format is used for name generation.
    if month_format == 'short':
        playlist_name = playlist_date.strftime('%b %Y')
    else:
        playlist_name = playlist_date.strftime('%B %Y')

    return playlist_name


def assert_playlist_does_not_exist(playlist_name='', spotify_data=None):
    """Assert that a playlist with the supplied name does not already exist.

    Args:
        playlist_name: A string with the name of the playlist to check for.
        spotify_data: A Spotify object containing the user's Spotify data.
    """

    # Catch the case where no spotify data is supplied.
    if not spotify_data:
        abort_script(error_message='No Spotify data supplied!')

    # Initially assume the playlist does not exist.
    playlist_exists = False
    
    # Extract the user's existing playlist's into a list.
    dictionary_of_playlist_data = spotify_data.current_user_playlists().items()
    list_of_users_playlists = spotify_data.current_user_playlists()['items']
    playlists_total = len(list_of_users_playlists)
    playlists_left = playlists_total

    # Make sure the monthly playlist does not already exist.
    while playlists_left:
        current_playlist = playlists_total - playlists_left
        if playlist_name == list_of_users_playlists[current_playlist]['name']:
            abort_script('A playlist called ' + playlist_name + ' already exists!')
        playlists_left -= 1


def get_most_played_songs(spotify_data=None, limit=50):
    """Use the user's credentials to request their most listened to songs.

    Args:
        spotify_data: A Spotify object containing the user's Spotify data.
    
    Returns:
        most_played_songs: The most listened to songs of the past month.
    """

    # Catch the case where no Spotify data is supplied.
    if not spotify_data:
        abort_script(error_message='No Spotify data supplied!')

    # Extract all Spotify track ID's using list comprehension.
    most_played_songs = [song['uri'] for song in spotify_data.
            current_user_top_tracks(time_range='short_term', limit=limit)['items']]

    return most_played_songs


def generate_playlist(tracks=None, spotify_data=None, playlist_date=None, title_format='short'):
    """Create a Spotify playlist of the user's currently most played tracks.

    Args:
        tracks: A list of the user's currently most played tracks on Spotify.
        spotify_data: A Spotify object containing the user's Spotify data.
        playlist_date: The date of the playlist being created.
    """

    # Catch the case where no list of tracks is supplied.
    if not tracks:
        abort_script(error_message='No list of tracks supplied!')
    
    # Catch the case where no Spotify data is supplied.
    if not spotify_data:
        abort_script(error_message='No Spotify data supplied!')

    # Catch the case where no playlist date is supplied.
    if not playlist_date:
        playlist_date = generate_playlist_date()

    # Song total could be less than the supplied limit.
    songs_total = len(tracks)

    # Determine the start of the playlist's description.
    if songs_total == 1:
        description = 'My top most played song of '
    else:
        description = 'My top ' + str(songs_total) + ' most played songs of '

    # Get both the short and long versions of the playlist name; either may be required.
    name_short = generate_playlist_name(playlist_date=playlist_date, month_format='short')
    name_long = generate_playlist_name(playlist_date=playlist_date, month_format='long')
    if title_format == 'short':
        name_for_description = name_short
    else:
        name_for_description = name_long
    description = (description
                   + name_for_description
                   + '. Auto-generated with A.M.M.O. '
                   + 'Visit https://github.com/JayMassey98 for more information.')
    
    # Auto-generate the playlist and add the determined songs to it.
    user = spotify_data.current_user()['id']
    is_playlist_public = True
    spotify_data.user_playlist_create(user=user,
                                      name=name_short,
                                      public=is_playlist_public,
                                      description=description)
    playlist_id = spotify_data.user_playlists(user=user)['items'][0]['id']
    spotify_data.user_playlist_add_tracks(user=user,
                                          playlist_id=playlist_id,
                                          tracks=tracks)


def main():
    """The entry point for this script, which will generate a Spotify playlist
    containing the user's most played songs on Spotify within the past month.
    """

    # Perform any required setup.
    set_environment_variables()
        
    # Get the playlist requirements.
    spotify_data = get_spotify_data()
    playlist_date = generate_playlist_date()
    playlist_name = generate_playlist_name(playlist_date=playlist_date,
                                           month_format='short')

    # Stop the script if the playlist already exists.
    assert_playlist_does_not_exist(playlist_name=playlist_name,
                                   spotify_data=spotify_data)

    # Generate the playlist with the user's most played songs.
    most_played_songs = get_most_played_songs(spotify_data=spotify_data)
    generate_playlist(tracks=most_played_songs,
                      spotify_data=spotify_data,
                      playlist_date=playlist_date)


# Run if called directly.
if __name__ == '__main__':
    main()