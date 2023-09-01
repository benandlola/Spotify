import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import config

scope = 'user-library-read playlist-modify-public playlist-modify-private user-top-read user-read-recently-played playlist-read-private playlist-read-collaborative'

def getToken():
    # Get access token
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config.client_id,client_secret=config.client_secret,redirect_uri=config.redirect_uri,scope=scope))

def getUser():
    return spotify.current_user()['id']

def getTopTracks(spotify, time_range):
    return spotify.current_user_top_tracks(time_range=time_range)

def createPlaylist(spotify, time_range):
    tracks = getTopTracks(spotify, time_range)
    playlist_name = time_range + " top tracks"
    playlists = spotify.current_user_playlists()
    # Don't add duplicates
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            return
    playlist = spotify.user_playlist_create(user=user, name=playlist_name, public=False)
    track_uris = [track['uri'] for track in tracks['items']]
    spotify.playlist_add_items(playlist_id=playlist['id'], items=track_uris)

if __name__ == "__main__":
    spotify = getToken()
    user = getUser()
    for time_range in ['short_term', 'medium_term', 'long_term']:
        createPlaylist(spotify, time_range)
    