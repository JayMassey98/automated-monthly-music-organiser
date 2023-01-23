"""Generate a Spotify playlist containing your top 50 songs of the past month.

Usage:
    python ammo.py <Client ID> <Client Secret> <Redirect URI> <username> <scope>
    TODO: Arguments have not yet been created; these are currently hard-coded.

Outline:
    Authenticate the user's Spotify credentials to allow the script to work.
    Check if a playlist exists for the past month, exiting the script if so.
    Use the user's credentials to pull HTML data containing their top songs.
    Jump to the 4th ol in the parsed HTML, which contains the relevant data.
    Store the nested il elements as a list, stripping irrelevant characters.
    Send the user's list of songs to the Spotify API to generate a playlist.

References:
    See https://developer.spotify.com/documentation/web-api/ for API info.
"""

import sys
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy import SpotifyOAuth
from datetime import date


def abort_script(error_message='An error has occurred!'):

    error_message = error_message + ' Script aborted.\n\n'
    sys.exit(error_message)


def get_spotify_data():

    # Set up the variables in order to request
    scope = 'playlist-modify-public'        # NOTE: Should this be an argument?
    username = '21js3bu3h7ixjemm7ypamzlga'  # NOTE: This should be an argument.
    client_id = None        # NOTE: Currently hard-coded via setx on my home PC.
    client_secret = None    # NOTE: Currently hard-coded via setx on my home PC.
    redirect_uri = None     # NOTE: Currently hard-coded via setx on my home PC.

    # Provide authentication for requested Spotify data.
    auth_manager = SpotifyOAuth(scope=scope, username=username)
    spotify_data = spotipy.Spotify(auth_manager=auth_manager)

    return spotify_data


def generate_playlist_date(todays_date=None):

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

    # Catch the case where no playlist date is supplied.
    if not playlist_date:
        abort_script(error_message='No playlist date supplied!')

    if month_length == 'short':
        playlist_name = playlist_date.strftime('%b %Y')
    else:
        playlist_name = playlist_date.strftime('%B %Y')

    return playlist_name


def assert_playlist_does_not_exist(playlist_name='', spotify_data=None):

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


def get_most_played_songs():

    # Headers taken from Chrome's inspect element of favoritemusic.guru.
    headers = {
        'authority': 'favoritemusic.guru',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    }

    # Cookies taken from Chrome's inspect element of favoritemusic.guru.
    cookies = {
        'spotifyTopsId': 'fdf56acc-b7d0-4cf2-8753-66bfc9f1d7a0',
    }

    # NOTE: Website could be changed in the future.
    url = 'https://favoritemusic.guru/'

    # Authenticate the user's Spotify credentials to allow the script to work.
    website_response = requests.get(url, headers=headers, cookies=cookies)
    if website_response.status_code != 200:
        abort_script('Failed to reach ' + url + '!')

    # Strip irrelevant data so that the list of songs can be sent to Spotify.
    extracted_html = BeautifulSoup(website_response.content, 'html.parser')
    list_of_ols = extracted_html.find_all('ol')
    past_month_data = 3     # NOTE: Could utilise other data in the future.
    most_played_songs = list_of_ols[past_month_data].contents
    most_played_songs = [song.text.replace('—', '') for song in most_played_songs]
    most_played_songs = [song.replace('\xa0', '') for song in most_played_songs]

    return most_played_songs


def generate_playlist(most_played_songs=[], playlist_date=None, spotify_data=None):
    
    # Catch the case where no list of songs is supplied.
    if not most_played_songs:
        abort_script(error_message='No songs supplied!')

    # Catch the case where no playlist date is supplied.
    if not playlist_date:
        abort_script(error_message='No playlist date supplied!')
    
    # Catch the case where no Spotify data is supplied.
    if not spotify_data:
        abort_script(error_message='No Spotify data supplied!')

    # TODO: Replace this line with an argument.
    username = '21js3bu3h7ixjemm7ypamzlga'

    # Number of songs saved, in-case less than 50 songs are supplied.
    songs_total = len(most_played_songs)
    songs_left = songs_total
     
    # Determine the start of the playlist's description.
    if songs_total == 1:
        playlist_description = 'My top most played song of '
    else:
        playlist_description = 'My top ' + str(songs_total) + ' most played songs of '

    # Get both the short and long versions of the playlist name.
    playlist_name_short = generate_playlist_name(playlist_date=playlist_date, month_length='short')
    playlist_name_long = generate_playlist_name(playlist_date=playlist_date, month_length='long')

    # Auto-generate and update the playlist's description.
    playlist_description = playlist_description + playlist_name_long + '. Auto-generated with A.M.M.O. Visit https://github.com/JayMassey98 for more information.'
    spotify_data.user_playlist_create(user=username,name=playlist_name_short,public=True,description=playlist_description)

    # Continue looping until all songs have been appended.
    while songs_left:
        current_song = songs_total - songs_left

        # TODO: Relocate this line to its own separate function.
        # This can break the code if certain characters are used.
        # Extra unit testing will then determine how to fix this.
        result = spotify_data.search(q=most_played_songs[current_song])

        most_played_songs[current_song] = result['tracks']['items'][0]['uri']
        songs_left -= 1;

    # Add the determined songs into the generated playlist.
    playlist = spotify_data.user_playlists(user=username)['items'][0]['id']
    spotify_data.user_playlist_add_tracks(user=username,playlist_id=playlist,tracks=most_played_songs)


def main():
        
    # Get the playlist requirements.
    spotify_data = get_spotify_data()
    playlist_date = generate_playlist_date()
    playlist_name = generate_playlist_name(playlist_date=playlist_date, month_length='long')

    # Stops the script if the playlist already exists.
    assert_playlist_does_not_exist(playlist_name=playlist_name, spotify_data=spotify_data)

    # Generate the playlist with your most played songs.
    most_played_songs = get_most_played_songs()
    generate_playlist(most_played_songs=most_played_songs, playlist_date=playlist_date, spotify_data=spotify_data)


# Only runs if called directly.
if __name__ == '__main__':
    main()