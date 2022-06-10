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

    # TODO: Add Spotify API calls in order to generate Spotify playlists.


# Only runs if called directly.
if __name__ == '__main__':
    main()