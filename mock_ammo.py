"""Mocks all external dependencies for ammo.py for testing purposes.

Outline:
    This code is used primarily for testing ammo.py within test_ammo.py, however
    it is also callable within ammo.py if the argument --dry_run is set to True.

References:
    https://developer.spotify.com/documentation/web-api/ for Spotify API info.
"""


# ----------------
# Mock Spotify API
# ----------------


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
        return {'items': [{'id': 'mock_playlist_uri_code'}]}
    def user_playlist_create(self, user, name, public, description):
        return {'id': 'mock_playlist_uri_code'}
    def playlist_add_items(self, playlist_id, items):
        pass


# Create a mock SpotifyOAuth class that uses a mock Spotify client.
class mock_SpotifyOAuth(mock_SpotifyClient):
    def __init__(self, *args, **kwargs):
        self.client = mock_SpotifyClient()
        self._session = None


# Create a mock Spotipy class to emulate Spotify API functionality.
class mock_spotipy():
    def Spotify(auth_manager=None):
        return mock_SpotifyOAuth(mock_SpotifyClient)
    class SpotifyOAuth(mock_SpotifyOAuth):
        pass