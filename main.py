import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import config

scope = 'user-library-read user-top-read playlist-modify-private playlist-modify-public'

def getToken():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config.client_id,client_secret=config.client_secret,redirect_uri=config.redirect_uri,scope=scope))

spotify = getToken()