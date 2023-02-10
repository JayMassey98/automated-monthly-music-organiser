"""Tests all the functionalities inside the ammo.py, which are used to generate
a Spotify playlist containing a user's most played songs of the previous month.

Usage:
    cmd /c "pytest -v --no-header ../test_ammo.py & pytest -v --no-header
    ../test_ammo.py > ../test_ammo.log"

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



# -----------------
# Spotify API Mocks
# -----------------


# Create a mock Spotify client containing various playlist functions.
class mock_SpotifyClient():
    def user(self):
        return 'mock_user'
    def current_user(self):
        return {'id': 'user_id'}
    def current_user_playlists(self):
        return {'items': [{'name': 'existing_playlist'}]}
    def current_user_top_tracks(self, time_range, limit):
        return {'items': [{'uri': 'track_id'}] * limit}
    def user_playlists(self, user):
        return {'items': [{'id': 'playlist_id'}]}
    def user_playlist_create(self, user, name, public, description):
        return {'id': 'new_playlist_id'}
    def playlist_add_items(self, playlist_id, items):
        pass


# Create a mock SpotifyOAuth class that returns a mock Spotify client.
class mock_SpotifyOAuth(mock_SpotifyClient):
    def __init__(self, *args, **kwargs):
        self.client = mock_SpotifyClient()
        self._session = None



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



# ---------------------
# test_check_connection
# ---------------------


# Test nothing happens if the received URL status code is 400.
def test_check_connection_returned_400_code(capfd):
    
    # Assert a connection can be established.
    url = 'https://api.spotify.com'
    assert check_connection(url) == None

    # Pytest provided 'capfd' allows capturing console prints.
    output, error = capfd.readouterr()
    assert output == ('Connected to https://api.spotify.com.\n')
    assert error == ''


# Test the script stops if a non-400 status code is received.
def test_check_connection_unknown_error_code(capfd):
    
    # Assert a connection cannot be established.
    url = 'error'
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_connection(url)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1

    # Pytest provided 'capfd' allows capturing console prints.
    output, error = capfd.readouterr()
    assert output == ('Error: An unknown error occurred when attempting to reach error.\n')
    assert error == '' # No system error here, as the resulting behavior above is expected.



# ---------------------------
# test_generate_playlist_name
# ---------------------------


# Test generating the playlist name when the current month is January.
def test_generate_playlist_name_for_january():
    ending_date = date(2023, 1, 1)
    playlist_date = ending_date.replace(year=2022, month=12)
    expected_playlist_name = playlist_date.replace(year=2022, month=12).strftime('%b %Y')
    generated_playlist_name = generate_playlist_name(ending_date=ending_date, month_format = 'short')
    assert generated_playlist_name == expected_playlist_name


# Test generating the playlist name when the current month is not January.
def test_generate_playlist_name_not_january(month=2):
    ending_date = date(2023, month, 1)
    playlist_date = ending_date.replace(month=month-1)
    expected_playlist_name = playlist_date.replace(month=month-1).strftime('%b %Y')
    generated_playlist_name = generate_playlist_name(ending_date=ending_date, month_format = 'short')
    assert generated_playlist_name == expected_playlist_name


# Test generating the playlist name for all months in the year.
def test_generate_playlist_name_all_months():

    # Test once for each month in the year.
    test_generate_playlist_name_for_january()
    for month in range(1, 12):
        test_generate_playlist_name_not_january(month + 1)


# Test generating the playlist name without any abbreviation.
def test_generate_playlist_name_long_format(month=2):
    ending_date = date(2023, month, 1)
    playlist_date = ending_date.replace(month=month-1)
    expected_playlist_name = playlist_date.replace(month=month-1).strftime('%B %Y')
    generated_playlist_name = generate_playlist_name(ending_date=ending_date, month_format = 'long')
    assert generated_playlist_name == expected_playlist_name



# -----------------------------
# test_check_if_playlist_exists
# -----------------------------


# Test the function raises an exception when no spotify data is supplied.
def test_check_if_playlist_exists_no_data():
    with pytest.raises(ValueError) as expected_error:
        check_if_playlist_exists()
    assert str(expected_error.value) == 'No Spotify data supplied!'


# Test the function raises an exception when the playlist already exists.
def test_check_if_playlist_exists_is_true():
    spotify_data = mock_SpotifyOAuth().client
    with pytest.raises(ValueError) as expected_error:
        check_if_playlist_exists(playlist_name='existing_playlist', spotify_data=spotify_data)
    assert str(expected_error.value) == 'A playlist called existing_playlist already exists!'


# Test the function does not raise an exception when the playlist does not already exist.
def test_check_if_playlist_exists_is_false():
    spotify_data = mock_SpotifyOAuth().client
    check_if_playlist_exists(playlist_name='new_playlist', spotify_data=spotify_data)
    assert True


# Test the function creates a duplicate playlist if it is allowed to do so.
def test_check_if_playlist_exists_allowed(capfd):
    spotify_data = mock_SpotifyOAuth().client
    check_if_playlist_exists(playlist_name='existing_playlist',
                             spotify_data=spotify_data,
                             duplicates_allowed=True)

    # Pytest provided 'capfd' allows capturing console prints.
    output, error = capfd.readouterr()
    assert output == ('A playlist called existing_playlist already exists!\n' +
                      'Creating another playlist called existing_playlist.\n')
    assert error == ''


# ---------------------------
# test_get_most_played_tracks
# ---------------------------


# Test the function raises an exception when no spotify data is supplied.
def test_get_most_played_tracks_no_data():
    with pytest.raises(ValueError) as expected_error:
        get_most_played_tracks()
    assert str(expected_error.value) == 'No Spotify data supplied!'


# Test the function returns a list of tracks.
def test_get_most_played_tracks_from_data():
    spotify_data = mock_SpotifyOAuth().client
    most_played_tracks = get_most_played_tracks(
        spotify_data=spotify_data)
    assert type(most_played_tracks) is list


# Test the function requests and receives 25 tracks.
def test_get_most_played_tracks_25_tracks():
    spotify_data = mock_SpotifyOAuth().client
    tracks_total = 25
    most_played_tracks = get_most_played_tracks(
        spotify_data=spotify_data,
        tracks_total=tracks_total)
    assert len(most_played_tracks) == tracks_total


# Test the function requests and receives 50 tracks.
def test_get_most_played_tracks_50_tracks():
    spotify_data = mock_SpotifyOAuth().client
    tracks_total = 50
    most_played_tracks = get_most_played_tracks(
        spotify_data=spotify_data,
        tracks_total=tracks_total)
    assert len(most_played_tracks) == tracks_total


# Test the function defaults to using 50 tracks if an invalid value is supplied.
def test_get_most_played_tracks_100_tracks(capfd):
    spotify_data = mock_SpotifyOAuth().client
    tracks_total = 100
    most_played_tracks = get_most_played_tracks(
        spotify_data=spotify_data,
        tracks_total=tracks_total)
    assert len(most_played_tracks) == 50

    # Pytest provided 'capfd' allows capturing console prints.
    output, error = capfd.readouterr()
    assert output == ('An invalid number of tracks has been requested!\n' +
                      'Switched to the default request of 50 tracks.\n')
    assert error == ''
    


# ------------------------------
# test_generate_spotify_playlist
# ------------------------------


# Test the function raises an exception when no list of tracks is supplied.
def test_generate_spotify_playlist_no_tracks():
    with pytest.raises(ValueError) as expected_error:
        generate_spotify_playlist()
    assert str(expected_error.value) == 'No list of tracks supplied!'


# Test the function raises an exception when no Spotify data is supplied.
def test_generate_spotify_playlist_no_data():
    tracks = ['song_1', 'song_2', 'song_3']
    with pytest.raises(ValueError) as expected_error:
        generate_spotify_playlist(tracks=tracks)
    assert str(expected_error.value) == 'No Spotify data supplied!'


# Test generating Spotify playlists correctly.
def test_generate_spotify_playlist_from_data():

    # Create mock inputs.
    tracks = ['song_1', 'song_2', 'song_3']
    spotify_data = mock_SpotifyOAuth().client
    ending_date = date(2023, 2, 1)

    # Test the function can be called.
    generate_spotify_playlist(
        tracks=tracks,
        spotify_data=spotify_data,
        ending_date=ending_date)



# ---------
# test_main
# ---------


# Test ammo.py can be run from start to finish.
def test_main_start_to_finish_is_successful():

    # Back up the real system arguments.
    sys_argv_bak = sys.argv

    # Ensure that the script can always create playlists.
    sys.argv = ['ammo.py', '--duplicates_allowed', 'True']

    # Test the script works.
    assert main() == None

    # Reinstate the arguments.
    sys.argv = sys_argv_bak