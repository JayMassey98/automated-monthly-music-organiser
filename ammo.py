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

TODO:
    Arguments for ammo.py are currently hard-coded instead of being supplied:
    <Client ID>, <Client Secret>, <Redirect URI>, <username>, and <scope>.
    Fix the doc-strings for each function so that they all match up properly.
"""

# Built-In Libraries
from datetime import date
import sys

# External Libraries
from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError
import spotipy
from spotipy import SpotifyOAuth


def abort_script(error_message='An error has occurred!'):
    """Exits the script after displaying an error message.

    Args:
        error_message: A string describing the error that has occurred.
    """

    error_message = error_message + ' Script aborted.\n\n'
    sys.exit(error_message)


def get_spotify_data():
    """Authenticate the user's Spotify credentials to allow data transfer.
    
    Returns:
        spotify_data: A Spotify object containing the user's Spotify data.

    Todo:
        Convert the following variables into supplied arguments.
    """

    # Set up the variables in order to request
    username = '21js3bu3h7ixjemm7ypamzlga'  # NOTE: This should be an argument.
    client_id = None        # NOTE: Currently hard-coded via setx on my home PC.
    client_secret = None    # NOTE: Currently hard-coded via setx on my home PC.
    redirect_uri = None     # NOTE: Currently hard-coded via setx on my home PC.

    # Provide the required authentication scopes to receive the requested Spotify data.
    auth_manager = SpotifyOAuth(scope='user-top-read playlist-modify-public', username=username)
    spotify_data = spotipy.Spotify(auth_manager=auth_manager)

    return spotify_data


def generate_playlist_date(todays_date=None):
    """Generates the date of the playlist being created.

    Args:
        todays_date: The date that the function is being run on.

    Returns:
        playlist_date: The date of the playlist being created.
    """

    # Determine the current date.
    if todays_date == None:
        todays_date = date.today()
    month = todays_date.month
    year = todays_date.year

    # Use the above to calculate the playlist's start date and name.
    if month == 1:
        playlist_date = todays_date.replace(year=year-1, month=12)
    else:
        playlist_date = todays_date.replace(month=month-1)

    return playlist_date


def generate_playlist_name(playlist_date=None, month_length='short'):
    """Generate the name of a playlist based on the date supplied.

    Args:
        playlist_date: The date of the playlist being created.
        month_length: Determines how to display the chosen month.

    Returns:
        A string representing the name of the playlist.
    """

    # Catch the case where no playlist date is supplied.
    if not playlist_date:
        abort_script(error_message='No playlist date supplied!')

    if month_length == 'short':
        playlist_name = playlist_date.strftime('%b %Y')
    else:
        playlist_name = playlist_date.strftime('%B %Y')

    return playlist_name


def assert_playlist_does_not_exist(playlist_name='', spotify_data=None):
    """Asserts that a playlist with the supplied name does not already exist.

    Args:
        playlist_name: A string with the name of the playlist to check for.
        spotify_data: A Spotify object containing the user's Spotify data.
    """

    # Initially assume this playlist does not exist.
    playlist_exists = False

    # Catch the case where no spotify data is supplied.
    if not spotify_data:
        abort_script(error_message='No Spotify data supplied!')
    
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


def generate_playlist(most_played_songs=None, spotify_data=None, playlist_date=None, username=None):
    """Create a Spotify playlist containing the user's top songs of the month.

    Args:
        most_played_songs: The most listened to songs of the past month.
        spotify_data: A Spotify object containing the user's Spotify data.
        playlist_date: The date of the playlist being created.
        username: The username ID of the user running the script.
    """

    # Catch the case where no list of songs is supplied.
    if not playlist_date:
        abort_script(error_message='No list of songs supplied!')
    
    # Catch the case where no Spotify data is supplied.
    if not spotify_data:
        abort_script(error_message='No Spotify data supplied!')

    # Catch the case where no playlist date is supplied.
    if not playlist_date:
        abort_script(error_message='No playlist date supplied!')

    # Catch the case where no username ID is supplied.
    if not playlist_date:
        abort_script(error_message='No username ID supplied!')

    # Song total could be less than the supplied limit.
    songs_total = len(most_played_songs)

    # Determine the start of the playlist's description.
    if songs_total == 1:
        playlist_description = 'My top most played song of '
    else:
        playlist_description = 'My top ' + str(songs_total) + ' most played songs of '

    # Get both the short and long versions of the playlist name for its description.
    playlist_name_short = generate_playlist_name(playlist_date=playlist_date, month_length='short')
    playlist_name_long = generate_playlist_name(playlist_date=playlist_date, month_length='long')
    playlist_description = playlist_description + playlist_name_long + '. Auto-generated with A.M.M.O. Visit https://github.com/JayMassey98 for more information.'

    # TODO: Replace this line with an argument.
    username = '21js3bu3h7ixjemm7ypamzlga'
    
    # Auto-generate the playlist and add the determined songs to it.
    spotify_data.user_playlist_create(user=username, name=playlist_name_short, public=True, description=playlist_description)
    generated_playlist = spotify_data.user_playlists(user=username)['items'][0]['id']
    spotify_data.user_playlist_add_tracks(user=username,playlist_id=generated_playlist,tracks=most_played_songs)


def main():
    """Serves as the entry point for the script, which generates a Spotify
    playlist consisting of a user's most played songs from the past month.
    """
        
    # Get the playlist requirements.
    spotify_data = get_spotify_data()
    playlist_date = generate_playlist_date()
    playlist_name = generate_playlist_name(playlist_date=playlist_date, month_length='short')

    # Stops the script if the playlist already exists.
    assert_playlist_does_not_exist(playlist_name=playlist_name, spotify_data=spotify_data)

    # Generate the playlist with your most played songs.
    most_played_songs = get_most_played_songs(spotify_data=spotify_data)
    generate_playlist(most_played_songs=most_played_songs, spotify_data=spotify_data,
                      playlist_date=playlist_date, username=None)


# Only runs if called directly.
if __name__ == '__main__':
    main()