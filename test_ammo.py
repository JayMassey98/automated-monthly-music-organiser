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