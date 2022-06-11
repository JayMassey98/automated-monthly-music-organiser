"""Generate a Spotify playlist containing your top 50 songs of the past month.

Usage:
    python ammo.py <Client ID> <Client Secret> <Redirect URI>

Outline:
    Authenticate Spotify credentials to access https://favoritemusic.guru/.
    Jump to the 4th ol in the pulled data, which contains the relevant data.
    Store the nested il elements as a list, stripping irrelevant characters.
    Send the contents of the list to the Spotify API to generate a playlist.

References:
    See https://developer.spotify.com/documentation/web-api/ for API info.
"""

import sys
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy import SpotifyOAuth


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
    list_of_ols = extracted_html.find_all('ol')
    past_month_data = 3     # NOTE: Could utilise other data in the future.
    list_of_songs = list_of_ols[past_month_data].contents

    # Strip irrelevant characters so that the data can be sent to Spotify.
    list_of_songs = [song.text.replace('—', '') for song in list_of_songs]
    list_of_songs = [song.replace('\xa0', '') for song in list_of_songs]

    # TODO: Convert the following into suppliable arguments.
    scope = 'playlist-modify-public'
    username = '21js3bu3h7ixjemm7ypamzlga'
    client_id = None        # NOTE: Currently hard coded via setx on my home PC.
    client_secret = None    # NOTE: Currently hard coded via setx on my home PC.
    redirect_uri = None     # NOTE: Currently hard coded via setx on my home PC.

    # Determine data for generating the Spotify data.
    token = SpotifyOAuth(scope=scope, username=username)
    spotify_data = spotipy.Spotify(auth_manager = token)

    # TODO: Replace name input with the current month and year.
    playlist_name = input('Enter a playlist name: ')
    month = '<month>'
    year = '<year>'

    # Produce a description for the generated playlist.
    playlist_description = 'My top 50 most played songs of ' + month + ' ' + year + '. Auto-generated with A.M.M.O. Visit https://github.com/JayMassey98 for more information.'
    spotify_data.user_playlist_create(user=username,name=playlist_name,public=True,description=playlist_description)

    # TODO: Replace manual inputting of songs with the list pulled from favoritemusic.guru.
    user_input = input('Select a song to add: ')
    list_of_songs = []

    # Continue looping until the user decides to stop.
    while user_input != 'stop':
        result = spotify_data.search(q=user_input)
        list_of_songs.append(result['tracks']['items'][0]['uri'])
        user_input = input('Select a song to add: ')

    # Get the generated playlist.
    playlist = spotify_data.user_playlists(user=username)['items'][0]['id']

    # Add the list of songs.
    if len(list_of_songs): # Prevents a null list error.
        spotify_data.user_playlist_add_tracks(user=username,playlist_id=playlist,tracks=list_of_songs)


# Only runs if called directly.
if __name__ == '__main__':
    main()