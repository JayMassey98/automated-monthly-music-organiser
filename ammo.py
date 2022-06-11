"""Generate a Spotify playlist containing your top 50 songs of the past month.

Usage:
    python ammo.py <Client ID> <Client Secret> <Redirect URI>

Outline:
    Authenticate Spotify credentials to access https://favoritemusic.guru/.
    Jump to the 4th ol in the pulled data, which contains the relevant data.
    Store the nested il elements as a list, stripping irrelevant characters.
    Check if a playlist exists for the past month, exiting the script if so.
    Send the contents of the list to the Spotify API to generate a playlist.

References:
    See https://developer.spotify.com/documentation/web-api/ for API info.
"""

import sys
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy import SpotifyOAuth
from datetime import date


def main():
    # TODO: Split main() into separate functions, then add Docstring comments.

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

    # Authenticate Spotify credentials to access https://favoritemusic.guru/.
    website_response = requests.get('https://favoritemusic.guru/', headers=headers, cookies=cookies)
    extracted_html = BeautifulSoup(website_response.content, 'html.parser')
    # TODO: Check that the response code is 200 and handle other possible cases.
    list_of_ols = extracted_html.find_all('ol')
    past_month_data = 3     # NOTE: Could utilise other data in the future.
    list_of_songs = list_of_ols[past_month_data].contents

    # Failsafe variables just in-case 50 songs have not been supplied.
    songs_total = len(list_of_songs)
    songs_left = songs_total

    # Strip irrelevant characters so that the data can be sent to Spotify.
    list_of_songs = [song.text.replace('—', '') for song in list_of_songs]
    list_of_songs = [song.replace('\xa0', '') for song in list_of_songs]

    # TODO: Convert the following into suppliable arguments.
    scope = 'playlist-modify-public'
    username = '21js3bu3h7ixjemm7ypamzlga'
    client_id = None        # NOTE: Currently hard coded via setx on my home PC.
    client_secret = None    # NOTE: Currently hard coded via setx on my home PC.
    redirect_uri = None     # NOTE: Currently hard coded via setx on my home PC.

    # Provide authentication to allow requesting Spotify data.
    token = SpotifyOAuth(scope=scope, username=username)
    spotify_data = spotipy.Spotify(auth_manager = token)

    # Determine the current date.
    todays_date = date.today()
    month = todays_date.month
    year = todays_date.year

    # Use the above to calculate the playlist's start date and name.
    month -= 1
    playlist_date = todays_date.replace(month=month)
    if not month:
        year -= 1
        playlist_date = todays_date.replace(month=12)
        playlist_date = todays_date.replace(year=year)
    playlist_name = playlist_date.strftime('%b %Y')

    # Extract the user's existing playlists into a list.
    dictionary_of_playlist_data = spotify_data.current_user_playlists().items()
    list_of_users_playlists = list(dictionary_of_playlist_data)[1][1]
    playlists_total = len(list_of_users_playlists)
    playlists_left = playlists_total

    # Make sure the monthly playlist does not already exist.
    while playlists_left:
        current_playlist = playlists_total - playlists_left
        if playlist_name == list_of_users_playlists[current_playlist]['name']:
            sys.exit('A playlist called ' + playlist_name + ' already exists! Aborting script.')
        playlists_left -= 1
     
    # Auto-generate the description of the playlist.
    playlist_description = 'My top 50 most played songs of ' + playlist_date.strftime('%B %Y') + '. Auto-generated with A.M.M.O. Visit https://github.com/JayMassey98 for more information.'
    spotify_data.user_playlist_create(user=username,name=playlist_name,public=True,description=playlist_description)

    # Continue looping until all songs have been appended.
    while songs_left:
        current_song = songs_total - songs_left
        result = spotify_data.search(q=list_of_songs[current_song])
        list_of_songs[current_song] = result['tracks']['items'][0]['uri']
        songs_left -= 1;

    # Get the generated playlist.
    playlist = spotify_data.user_playlists(user=username)['items'][0]['id']

    # Add the list of songs.
    if len(list_of_songs): # Prevents a null list error.
        spotify_data.user_playlist_add_tracks(user=username,playlist_id=playlist,tracks=list_of_songs)


# Only runs if called directly.
if __name__ == '__main__':
    main()