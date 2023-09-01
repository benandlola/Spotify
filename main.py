
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import config

def requestAccess():
    url = config.url+'/token'
    headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
    payload = {'grant_type' : 'client_credentials',
                'client_id' : config.client_id,
                'client_secret' : config.secret_id}
    response = requests.post(url, headers=headers, data=payload).json()
    return response['access_token']

access_token = requestAccess()