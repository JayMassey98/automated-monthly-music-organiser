"""Generates a Spotify playlist containing your top 50 songs of the past month.

Usage:
    python ../ammo.py

Outline:
    This script retrieves the necessary information required to create a Spotify
    playlist, such as a user's data, the playlist date, and its subsequent name.
    After asserting that a playlist with the chosen name does not already exist,
    one is generated with the user's most played songs from the previous month.

References:
    https://developer.spotify.com/documentation/web-api/ for Spotify API info.
"""

# Built-In Libraries
import argparse
from datetime import date
import os
import sys

# External Libraries
import mock_ammo
import requests
import spotipy


def set_environment_variables():
    """Set environment variables required for the Spotipy library."""
    
    # All the required Spotipy environment variables.
    environment_variables = {
        'SPOTIPY_CLIENT_ID': 'Client ID: ',
        'SPOTIPY_CLIENT_SECRET': 'Client Secret: ',
        'SPOTIPY_REDIRECT_URI': 'Redirect URI: '
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
    parser.add_argument('-d',
                        '--dry_run',
                        help='Determines if the Spotify API should be mocked.',
                        type=bool,
                        default=False)
    parser.add_argument('-m',
                        '--month_format',
                        help=('Determines how months are displayed in ' +
                              'generated playlists.'),
                        type=str,
                        default='short')
    parser.add_argument('-c',
                        '--copies_allowed',
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


def check_connection(url, dry_run=False):
    """Check if a supplied URL is reachable. If the URL cannot be reached, then
    the resulting error description will be printed and the script will halt.

    Args:
        url: The URL that the program will establish a connection with.
        dry_run: A boolean determining if external API should be mocked.
    """
    
    # Don't attempt a real connection for dry runs.
    if dry_run:
        print('Secured a ' + url + ' link.')
        return
    
    # Map status codes to their corresponding descriptions or boolean values.
    status_codes = {
        200: True,  # OK: The request was successful.
        201: True,  # Created: The request was successful and a resource was created.
        204: True,  # No Content: The request was successful but there is no representation to return.
        400: 'Bad Request: The request could not be understood or was missing required parameters.',
        401: 'Unauthorized: Authentication failed or user does not have permissions for the requested operation.',
        403: 'Forbidden: Authentication succeeded, but the authenticated user does not have access to the requested resource.',
        404: 'Not Found: The requested resource could not be found.',
        429: 'Too Many Requests: The user has sent too many requests in a given amount of time.',
        500: 'Internal Server Error: An error occurred on the server.',
        502: 'Bad Gateway: The server was acting as a gateway or proxy and received an invalid response from the upstream server.',
        503: 'Service Unavailable: The server is currently unavailable (because it is overloaded or down for maintenance).'
    }

    # Try to make a GET request to the URL.
    try:
        
        # Get the description for the status code.
        response = requests.get(url)
        status = status_codes.get(response.status_code)

        # If there is no description, tell the user and return.
        if status == True:
            print('Secured a ' + url + ' link.')
            return

        # If the status is a string, print the string.
        if isinstance(status, str):
            print(status)

    # Catch any exceptions that might occur while making the GET request.
    except requests.exceptions.RequestException:
        print('Error: An unknown error occurred when attempting to reach ' + url + '.')

    # No connection found; exit the script.
    sys.exit(1)


def get_spotify_data(dry_run=False):
    """Authenticate a user's Spotify credentials to allow data requests.
    
    Args:
        dry_run: A boolean determining if external API should be mocked.
    
    Returns:
        spotify_data: A Spotify object containing a user's Spotify data.
    """
    
    # Detach Spotipy on dry runs.
    if dry_run:
        SpotifyOAuth = mock_ammo.mock_spotipy.SpotifyOAuth
        Spotify = mock_ammo.mock_spotipy.Spotify
    else:
        SpotifyOAuth = spotipy.SpotifyOAuth
        Spotify = spotipy.Spotify

    # Supply the required scopes and retrieve the data.
    auth_manager = SpotifyOAuth(scope='user-top-read '
                                + 'playlist-modify-public '
                                + 'playlist-modify-private')
    spotify_data = Spotify(auth_manager=auth_manager)

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
                             copies_allowed=False):
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
        exist_output = f'{playlist_name} found on Spotify!'
        if copies_allowed:
            print('\nWarning: ' + exist_output +
                  f'\nCreating another {playlist_name} playlist.\n')
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

    # The number of tracks returned could be less than the requested total.
    print('A total of', len(most_played_tracks), 'songs have been selected.')
    
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
        print('The month will be titled in short form.')
    else:
        name_for_title = name_long
        print('The month will be titled in long form.')

    # Generate the description for the playlist.
    description = (description
                   + name_long
                   + '. Auto-generated with AMMO. Visit '
                   + 'https://github.com/JayMassey98'
                   + ' for more information.')
    
    # Generate the playlist and obtain its resulting ID.
    playlist_id = spotify_data.user_playlist_create(
        user=spotify_data.current_user()['id'],
        name=name_for_title,
        public=playlist_public,
        description=description
        )['id']
    print('Generating a playlist for ' + name_long + '.')

    # Add the tracks to the playlist.
    spotify_data.playlist_add_items(
        playlist_id=playlist_id,
        items=tracks)
    print('\nPlaylist successfully pushed to Spotify:')
    print('spotify:playlist:' + playlist_id)


def main():
    """The entry point for this script, which will generate a Spotify playlist
    containing the user's most played songs on Spotify within the past month.
    """

    # Output the title of the script into the console.
    print('Automated Monthly Music Organiser (AMMO)\n')

    # Perform required setup.
    set_environment_variables()
    args = get_optional_arguments()

    # Check the Spotify API can be reached.
    check_connection(
        url='https://api.spotify.com',
        dry_run=args.dry_run)
        
    # Get the playlist requirements.
    spotify_data = get_spotify_data(
        dry_run=args.dry_run)
    playlist_name = generate_playlist_name(
        month_format=args.month_format)

    # Stop the script if the playlist already exists.
    check_if_playlist_exists(
        playlist_name=playlist_name,
        spotify_data=spotify_data,
        copies_allowed=args.copies_allowed)

    # Get the user's recently most played tracks.
    most_played_tracks = get_most_played_tracks(
        spotify_data=spotify_data,
        tracks_total=args.tracks_total)

    # Generate a playlist with the supplied items.
    generate_spotify_playlist(
        tracks=most_played_tracks,
        spotify_data=spotify_data,
        month_format=args.month_format,
        playlist_public=args.playlist_public)


# Run if called directly.
if __name__ == '__main__':
    main()