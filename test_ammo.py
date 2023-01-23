"""Tests all the functionalities inside the ammo.py, which are used to generate
a Spotify playlist containing a user's most played songs of the previous month.

Usage:
    pytest -v ../test_ammo.py

Outline:
    Runs through each function, testing various possible cases for each.

References:
    See https://developer.spotify.com/documentation/web-api/ for API info.
"""

# Built-In Libraries
from datetime import date
import sys

# External Libraries
from ammo import *
import pytest
import spotipy
from spotipy import SpotifyOAuth



# -----------------
# Spotify API Mocks
# -----------------


# Creates a mock SpotifyOAuth class that returns a mock Spotify client.
class mock_SpotifyOAuth(SpotifyOAuth):
    def __init__(self, *args, **kwargs):
        self.client = mock_SpotifyClient()
        self._session = None


# Creates a mock Spotify client containing various playlist functions.
class mock_SpotifyClient():
    def user(self):
        return 'mock_user'
    def current_user_playlists(self):
        return {'items': [{'name': 'existing_playlist'}]}



# -----------------
# test_abort_script
# -----------------


# Tests aborting the script with the default error message.
def test_abort_script_default_error_message():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        abort_script()
    assert pytest_wrapped_e.value.code == 'An error has occurred! Script aborted.\n\n'


# Tests aborting the script with a custom error message.
def test_abort_script_custom_error_message():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        abort_script("Custom error message.")
    assert pytest_wrapped_e.value.code == 'Custom error message. Script aborted.\n\n'



# ---------------------------
# test_generate_playlist_name
# ---------------------------


# Tests generating the playlist name for all months in the year.
def test_generate_playlist_name_for_all_months():

    # Generate a playlist date first.
    generate_playlist_date()

    # Tests once for each month in the year.
    test_generate_playlist_name_for_only_january()
    for month in range(1, 12):
        test_generate_playlist_name_when_not_january(month + 1)


# Tests generating the playlist name when the current month is January.
def test_generate_playlist_name_for_only_january():
    mock_date = date(2023, 1, 1)
    mock_playlist_date = mock_date.replace(year=2022, month=12)
    expected_playlist_name = mock_date.replace(year=2022, month=12).strftime('%b %Y')
    generated_playlist_name = generate_playlist_name(playlist_date=mock_playlist_date, month_length = 'short')
    assert generated_playlist_name == expected_playlist_name


# Tests generating the playlist name when the current month is not January.
def test_generate_playlist_name_when_not_january(month=2):
    mock_date = date(2023, month, 1)
    mock_playlist_date = mock_date.replace(month=month-1)
    expected_playlist_name = mock_date.replace(month=month-1).strftime('%b %Y')
    generated_playlist_name = generate_playlist_name(playlist_date=mock_playlist_date, month_length = 'short')
    assert generated_playlist_name == expected_playlist_name


# Tests generating the playlist name without any abbreviation.
def test_generate_playlist_name_no_abbreviation(month=2):
    mock_date = date(2023, month, 1)
    mock_playlist_date = mock_date.replace(month=month-1)
    expected_playlist_name = mock_date.replace(month=month-1).strftime('%B %Y')
    generated_playlist_name = generate_playlist_name(playlist_date=mock_playlist_date, month_length = 'long')
    assert generated_playlist_name == expected_playlist_name



# -----------------------------------
# test_assert_playlist_does_not_exist
# -----------------------------------


# Tests the function raises an exception when no spotify data is supplied.
def test_assert_playlist_does_not_exist_no_data():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        assert_playlist_does_not_exist(playlist_name='existing_playlist')
    assert pytest_wrapped_e.value.code == 'No Spotify data supplied! Script aborted.\n\n'


# Tests the function raises an exception when the playlist already exists.
def test_assert_playlist_does_not_exist_is_false():
    spotify_data = mock_SpotifyOAuth().client
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        assert_playlist_does_not_exist(playlist_name='existing_playlist', spotify_data=spotify_data)
    assert pytest_wrapped_e.value.code == 'A playlist called existing_playlist already exists! Script aborted.\n\n'


# Tests the function does not raise an exception when the playlist does not already exist.
def test_assert_playlist_does_not_exist_is_true():
    spotify_data = mock_SpotifyOAuth().client
    assert_playlist_does_not_exist(playlist_name='new_playlist', spotify_data=spotify_data)
    assert True



# ----------------------
# test_generate_playlist
# ----------------------

# TODO: Add more tests that check mocked data.


# Tests a playlist is generated from the supplied Spotify data.
def test_generate_playlist():

    # Creates mock inputs.
    most_played_songs = ['song_1', 'song_2', 'song_3']
    playlist_date = generate_playlist_date()
    spotify_data = mock_SpotifyOAuth().client

    # Tests the function can be called.
    generate_playlist(
        most_played_songs=most_played_songs,
        playlist_date=playlist_date,
        spotify_data=spotify_data)

    # TODO: Examine the generated playlist.