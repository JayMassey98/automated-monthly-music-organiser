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


# Create a mock SpotifyOAuth class that returns a mock Spotify client.
class mock_SpotifyOAuth(SpotifyOAuth):
    def __init__(self, *args, **kwargs):
        self.client = mock_SpotifyClient()
        self._session = None


# Create a mock Spotify client containing various playlist functions.
class mock_SpotifyClient():
    def user(self):
        return 'mock_user'
    def current_user(self):
        return {'id': 'user_id'}
    def current_user_playlists(self):
        return {'items': [{'name': 'existing_playlist'}]}
    def current_user_top_tracks(self, time_range, limit):
        return {'items': [{'uri': 'track_id'}]}
    def user_playlists(self, user):
        return {'items': [{'id': 'playlist_id'}]}
    def user_playlist_create(self, user, name, public, description):
        return 'new_playlist'
    def user_playlist_add_tracks(self, user, playlist_id, tracks):
        pass



# -----------------
# test_abort_script
# -----------------


# Test aborting the script with the default error message.
def test_abort_script_default_error_message():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        abort_script()
    assert pytest_wrapped_e.value.code == 'An error has occurred! Script aborted.\n\n'


# Test aborting the script with a custom error message.
def test_abort_script_custom_error_message():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        abort_script("Custom error message.")
    assert pytest_wrapped_e.value.code == 'Custom error message. Script aborted.\n\n'



# --------------------------------------
# test_set_spotipy_environment_variables
# --------------------------------------


# Test all of the required environment variables being set.
def test_set_environment_variables_all_set(monkeypatch):

    # Set the environment variables before running the function below.
    monkeypatch.setenv("SPOTIPY_CLIENT_ID", 'test_client_id')
    monkeypatch.setenv("SPOTIPY_CLIENT_SECRET", 'test_client_secret')
    monkeypatch.setenv("SPOTIPY_REDIRECT_URI", 'test_redirect_uri')
    set_environment_variables()

    # Assert that the environment variables above are set correctly.
    assert os.environ['SPOTIPY_CLIENT_ID'] == 'test_client_id'
    assert os.environ['SPOTIPY_CLIENT_SECRET'] == 'test_client_secret'
    assert os.environ['SPOTIPY_REDIRECT_URI'] == 'test_redirect_uri'


# Test none of the required environment variables being set.
def test_set_environment_variables_none_set(monkeypatch):

    # Delete the environment variables without raising errors.
    monkeypatch.delenv("SPOTIPY_CLIENT_ID", raising=False)
    monkeypatch.delenv("SPOTIPY_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("SPOTIPY_REDIRECT_URI", raising=False)
    
    # Mock a user's input.
    def mock_input(prompt):
        if prompt == "Client ID: ":
            return "test_client_id"
        elif prompt == "Client Secret: ":
            return "test_client_secret"
        elif prompt == "Redirect URI: ":
            return "test_redirect_uri"

    # Mock the required user inputs via monkey-patching.
    monkeypatch.setattr('builtins.input', mock_input)
    set_environment_variables()

    # Assert that the mocked inputs are set as environment variables.
    assert os.environ['SPOTIPY_CLIENT_ID'] == 'test_client_id'
    assert os.environ['SPOTIPY_CLIENT_SECRET'] == 'test_client_secret'
    assert os.environ['SPOTIPY_REDIRECT_URI'] == 'test_redirect_uri'



# ---------------------------
# test_generate_playlist_name
# ---------------------------


# Test generating the playlist name when the current month is January.
def test_generate_playlist_name_for_january():
    mock_date = date(2023, 1, 1)
    mock_playlist_date = mock_date.replace(year=2022, month=12)
    expected_playlist_name = mock_date.replace(year=2022, month=12).strftime('%b %Y')
    generated_playlist_name = generate_playlist_name(playlist_date=mock_playlist_date, month_format = 'short')
    assert generated_playlist_name == expected_playlist_name


# Test generating the playlist name when the current month is not January.
def test_generate_playlist_name_not_january(month=2):
    mock_date = date(2023, month, 1)
    mock_playlist_date = mock_date.replace(month=month-1)
    expected_playlist_name = mock_date.replace(month=month-1).strftime('%b %Y')
    generated_playlist_name = generate_playlist_name(playlist_date=mock_playlist_date, month_format = 'short')
    assert generated_playlist_name == expected_playlist_name


# Test generating the playlist name for all months in the year.
def test_generate_playlist_name_for_all_months():

    # Generate a playlist date first.
    generate_playlist_date()

    # Test once for each month in the year.
    test_generate_playlist_name_for_january()
    for month in range(1, 12):
        test_generate_playlist_name_not_january(month + 1)


# Test generating the playlist name without any abbreviation.
def test_generate_playlist_name_no_abbreviation(month=2):
    mock_date = date(2023, month, 1)
    mock_playlist_date = mock_date.replace(month=month-1)
    expected_playlist_name = mock_date.replace(month=month-1).strftime('%B %Y')
    generated_playlist_name = generate_playlist_name(playlist_date=mock_playlist_date, month_format = 'long')
    assert generated_playlist_name == expected_playlist_name



# -----------------------------------
# test_assert_playlist_does_not_exist
# -----------------------------------


# Test the function raises an exception when no spotify data is supplied.
def test_assert_playlist_does_not_exist_no_data():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        assert_playlist_does_not_exist(playlist_name='existing_playlist')
    assert pytest_wrapped_e.value.code == 'No Spotify data supplied! Script aborted.\n\n'


# Test the function raises an exception when the playlist already exists.
def test_assert_playlist_does_not_exist_is_false():
    spotify_data = mock_SpotifyOAuth().client
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        assert_playlist_does_not_exist(playlist_name='existing_playlist', spotify_data=spotify_data)
    assert pytest_wrapped_e.value.code == 'A playlist called existing_playlist already exists! Script aborted.\n\n'


# Test the function does not raise an exception when the playlist does not already exist.
def test_assert_playlist_does_not_exist_is_true():
    spotify_data = mock_SpotifyOAuth().client
    assert_playlist_does_not_exist(playlist_name='new_playlist', spotify_data=spotify_data)
    assert True



# --------------------------
# test_get_most_played_songs
# --------------------------


# Test the function returns a list of equal or less length than supplied limit.
def test_get_most_played_songs():
    spotify_data = mock_SpotifyOAuth().client
    limit = 50
    most_played_songs = get_most_played_songs(spotify_data=spotify_data, limit=limit)
    assert type(most_played_songs) is list
    assert len(most_played_songs) <= limit
    


# ----------------------
# test_generate_playlist
# ----------------------


# Test a playlist is generated from the supplied Spotify data.
def test_generate_playlist():

    # Create mock inputs.
    most_played_songs = ['song_1', 'song_2', 'song_3']
    playlist_date = generate_playlist_date()
    spotify_data = mock_SpotifyOAuth().client

    # Test the function can be called.
    generate_playlist(
        most_played_songs=most_played_songs,
        playlist_date=playlist_date,
        spotify_data=spotify_data)
