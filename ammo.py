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
import argparse
from datetime import date
import os

# External Libraries
import spotipy
from spotipy import SpotifyOAuth


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


def get_optional_arguments():
    """Get any arguments that have been supplied, supplying defaults if not.
    
    Returns:
        args: A collection of arguments that can be supplied to the script.
    """

    # Call the argparse library to handle any supplied arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-m',
                        '--month_format',
                        help=('Determines how months are displayed in ' +
                              'generated playlists.'),
                        type=str,
                        default='short')
    parser.add_argument('-d',
                        '--duplicates_allowed',
                        help=('Determines if a playlist should be generated ' +
                              'if one with the same name already exists.'),
                        type=bool,
                        default=False)
    parser.add_argument('-t',
                        '--tracks_total',
                        help=('Determines the total number of tracks to use ' +
                              'in the generated playlist (between 1 and 50).'),
                        type=int,
                        default=50)
    parser.add_argument('-p',
                        '--playlist_public',
                        help='Determines if a playlist should be public.',
                        type=bool,
                        default=True)
    args = parser.parse_args()

    return args


def get_spotify_data():
    """Authenticate a user's Spotify credentials to allow data requests.
    
    Returns:
        spotify_data: A Spotify object containing a user's Spotify data.
    """

    # Provide the required authentication scopes for requesting Spotify data.
    auth_manager = SpotifyOAuth(scope='user-top-read '
                                + 'playlist-modify-public '
                                + 'playlist-modify-private')
    spotify_data = spotipy.Spotify(auth_manager=auth_manager)

    return spotify_data


def generate_playlist_name(ending_date=None, month_format='short'):
    """Generate the name of a playlist based on the date supplied.

    Args:
        ending_date: The end date that the function is being run for.
        month_format: A string that chooses how to display the month.

    Returns:
        playlist_name: A string that is a month prior to ending_date.
    """

    # Determine the current date.
    if not ending_date:
        ending_date = date.today()
    month = ending_date.month
    year = ending_date.year

    # Use the above to calculate the playlist's start date and name.
    if month == 1:
        playlist_date = ending_date.replace(year=year-1, month=12)
    else:
        playlist_date = ending_date.replace(month=month-1)

    # Choose which format is used for name generation.
    if month_format == 'short':
        playlist_name = playlist_date.strftime('%b %Y')
    else:
        playlist_name = playlist_date.strftime('%B %Y')

    return playlist_name


def check_if_playlist_exists(playlist_name='', spotify_data=None,
                             duplicates_allowed=False):
    """Check if the user already has a playlist with the supplied name.

    Args:
        playlist_name: A string with the name of the playlist to check for.
        spotify_data: A Spotify object containing the user's Spotify data.
    """

    # Catch the case where no spotify data is supplied.
    if not spotify_data:
        raise ValueError('No Spotify data supplied!')

    # Extract the user's existing playlists using list comprehension.
    existing_playlists = [playlist['name'] for playlist in
                          spotify_data.current_user_playlists()['items']]

    # Determine if a playlist should be made.
    if playlist_name in existing_playlists:
        exist_output = f'A playlist called {playlist_name} already exists!'
        if duplicates_allowed:
            print(exist_output +
                  f'\nCreating another playlist called {playlist_name}.')
        else:
            raise ValueError(exist_output)


def get_most_played_tracks(spotify_data=None, tracks_total=50):
    """Use the user's credentials to get ID's of their most listened tracks.

    Args:
        spotify_data: A Spotify object containing the user's Spotify data.
        tracks_total: An integer to determine how many tracks to retrieve.
    
    Returns:
        most_played_tracks: The user's most played tracks in the past month.
    """

    # Catch the case where no Spotify data is supplied.
    if not spotify_data:
        raise ValueError('No Spotify data supplied!')

    # Ensure the tracks total supplied is valid.
    if tracks_total is None or tracks_total < 1 or tracks_total > 50:
        tracks_total = 50
        print('An invalid number of tracks has been requested!\n' +
              f'Switched to the default request of {tracks_total} tracks.')

    # Extract all Spotify track ID's using list comprehension.
    most_played_tracks = [track['uri'] for track in spotify_data.
                         current_user_top_tracks(time_range='short_term',
                                                 limit=tracks_total)['items']]

    return most_played_tracks


def generate_spotify_playlist(tracks=None, spotify_data=None,
                              ending_date=None, month_format='short',
                              playlist_public=True):
    """Create a Spotify playlist of the user's currently most played tracks.

    Args:
        tracks: A list of the user's currently most played tracks on Spotify.
        spotify_data: A Spotify object containing the user's Spotify data.
        ending_date: The end date that the function is being run for.
        title_format: A string determining the playlist's title format.
    """

    # Catch the case where no list of tracks is supplied.
    if not tracks:
        raise ValueError('No list of tracks supplied!')
    
    # Catch the case where no Spotify data is supplied.
    if not spotify_data:
        raise ValueError('No Spotify data supplied!')

    # Catch the case where no ending date is supplied.
    ending_date = ending_date or date.today()

    # Determine the start of the playlist's description.
    tracks_total = len(tracks)
    if tracks_total == 1:
        description = 'My top most played song of '
    else:
        description = 'My top ' + str(tracks_total) + ' most played songs of '

    # Get playlist name formats (both are required).
    name_short = generate_playlist_name(
        ending_date=ending_date,
        month_format='short')
    name_long = generate_playlist_name(
        ending_date=ending_date,
        month_format='long')

    # Determine the description's name format.
    if month_format == 'short':
        name_for_title = name_short
    else:
        name_for_title = name_long

    # Generate the description for the playlist.
    description = (description
                   + name_long
                   + '. Auto-generated with A.M.M.O. Visit '
                   + 'https://github.com/JayMassey98'
                   + ' for more information.')
    
    # Generate the playlist and obtain its resulting ID.
    user = spotify_data.current_user()['id']
    playlist_id = spotify_data.user_playlist_create(
        user=user,
        name=name_for_title,
        public=playlist_public,
        description=description
        )['id']

    # Add the supplied tracks to the generated playlist.
    spotify_data.user_playlist_add_tracks(
        user=user,
        playlist_id=playlist_id,
        tracks=tracks)


def main():
    """The entry point for this script, which will generate a Spotify playlist
    containing the user's most played songs on Spotify within the past month.
    """

    # Perform required setup.
    set_environment_variables()
    args = get_optional_arguments()
        
    # Get the playlist requirements.
    spotify_data = get_spotify_data()
    playlist_date = generate_playlist_date()
    playlist_name = generate_playlist_name(
        playlist_date=playlist_date,
        month_format=args.month_format)

    # Stop the script if the playlist already exists.
    check_if_playlist_exists(
        playlist_name=playlist_name,
        spotify_data=spotify_data,
        duplicates_allowed=args.duplicates_allowed)

    # Get the user's recently most played tracks.
    most_played_tracks = get_most_played_tracks(
        spotify_data=spotify_data,
        tracks_total=args.tracks_total)

    # Generate a playlist with the supplied items.
    generate_spotify_playlist(
        tracks=most_played_tracks,
        spotify_data=spotify_data,
        playlist_date=playlist_date,
        month_format=args.month_format,
        playlist_public=args.playlist_public)


# Run if called directly.
if __name__ == '__main__':
    main()