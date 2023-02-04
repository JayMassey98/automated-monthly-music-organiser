# Backlog

* Add the option to create a playlist even if the name already exists
	* Change function name from 'assert_playlist_does_not_exist' to 'check_if_playlist_exists' and flip true's to false's and vice versa.

* Test '..._no_spotify_data' for each function that requires it.
	* Also test all the other input items such as 'most_played_tracks'.

* Add a note saying something like 'Note: The limit has been capped to the maximum of 50 songs.' when a number higher than 50 is used.

* Add a check that limit is a positive integer value between 1 and 50.
	* Add the ability to re-input the limit value if not.
	* Add the ability to re-input the limit value until it's accepted.

* Add the ability to generate short or long month format; by default this should be 'short'.

* Add the ability to make playlists public or not; by default this should be True.

* Add back in the items within "from requests.exceptions import HTTPError".










Added more options for the user when generating playlists.
Refactored generate_playlist(...) to allow more user options.

Started adding more options for user's generating their playlists.
Added more options for user's when they generate their playlists.
