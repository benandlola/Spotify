import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import config
from flask import Flask, url_for, session, request, redirect, render_template
import time

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'spotify-session'
app.secret_key = 'spotify_playlist_generator'

@app.route('/')
def login():
    return redirect(create_spotify_oauth().get_authorize_url())

@app.route('/redirect')
def redirect_page():
    session.clear()
    session['token_info'] = create_spotify_oauth().get_access_token(request.args.get('code'))
    return redirect(url_for('create_top_tracks_playlists')) #change to home

@app.route('/createTopTracksPlaylists')
def create_top_tracks_playlists():
    sp = validate()
    for time_range in ['short_term', 'medium_term', 'long_term']:
        tracks = sp.current_user_top_tracks(time_range=time_range, limit=50)
        if time_range == 'short_term': playlist_name = "Recently listened vibes"
        elif time_range == 'medium_term': playlist_name = "Throwback tracks"
        else: playlist_name = "All time favourites"
        playlists = sp.current_user_playlists()

        # Don't add duplicates 
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                existing_playlist = playlist
            
        # TODO recommended_tracks = spotify.recommendations(seed_tracks=track_uris)
        if existing_playlist: #instead update
            existing_tracks = sp.playlist_tracks(existing_playlist['id'])
            existing_track_uris = [track['track']['uri'] for track in existing_tracks['items']]
            track_uris = [track['uri'] for track in tracks['items']]
            tracks_to_add = list(set(track_uris) - set(existing_track_uris))
            tracks_to_remove = list(set(existing_track_uris) - set(track_uris))
            if tracks_to_remove:
                sp.playlist_remove_all_occurrences_of_items(existing_playlist['id'], tracks_to_remove)
            if tracks_to_add:
                sp.playlist_add_items(existing_playlist['id'], tracks_to_add)
                return(playlist_name + ' updated')
        else: #creating new playlist
            playlist = sp.user_playlist_create(user=sp.current_user()['id'], name=playlist_name, public=False)
            track_uris = [track['uri'] for track in tracks['items']]
            sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
            return(playlist_name + ' made')


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id=config.client_id,
            client_secret=config.client_secret,
            redirect_uri=url_for('redirect_page', _external=True),
            scope='user-library-read playlist-modify-public playlist-modify-private user-top-read user-read-recently-played playlist-read-private playlist-read-collaborative')

def get_token():
    token_info = session.get('token_info')
    if not token_info:
        redirect(url_for('login'))
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        token_info = create_spotify_oauth().refresh_access_token(token_info['refresh_token'])
    return token_info

def validate():
    try:
        token_info = get_token()
    except:
        return redirect('/')
    return spotipy.Spotify(auth=token_info['access_token'])

'''
def create_top_playlist(time_range):
    tracks = spotify.current_user_top_tracks(time_range=time_range, limit=50)
    if time_range == 'short_term':
        playlist_name = "Recently listened vibes"
    elif time_range == 'medium_term':
        playlist_name = "Throwback tracks"
    else:
        playlist_name = "All time favourites"
    playlists = spotify.current_user_playlists()

    # Don't add duplicates
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            existing_playlist = playlist
        
    # TODO recommended_tracks = spotify.recommendations(seed_tracks=track_uris)
    if existing_playlist:
        existing_tracks = sp.playlist_tracks(existing_playlist['id'])
        existing_track_uris = [track['track']['uri'] for track in existing_tracks['items']]
        tracks_to_add = list(set(new_track_uris) - set(existing_track_uris))
        tracks_to_remove = list(set(existing_track_uris) - set(new_track_uris))
        if tracks_to_remove:
            sp.playlist_remove_all_occurrences_of_items(existing_playlist['id'], tracks_to_remove)
        if tracks_to_add:
            sp.playlist_add_items(existing_playlist['id'], tracks_to_add)
            print(playlist_name + ' updated')
    else:
        playlist = spotify.user_playlist_create(user=user, name=playlist_name, public=False)
        track_uris = [track['uri'] for track in tracks['items']]
        spotify.playlist_add_items(playlist_id=playlist['id'], items=track_uris)

        print(playlist_name + ' made')

def get_all_saved_songs():
    offset = 0
    all_saved_tracks = []
    while True:
        saved_tracks = spotify.current_user_saved_tracks(limit=50, offset=offset)
        if not saved_tracks['items']:
            break  # No more tracks to retrieve
        all_saved_tracks.extend(saved_tracks['items'])
        offset += 50
    return all_saved_tracks

def creat_artist_playlist():
    top_artists = spotify.current_user_top_artists(time_range='long_term', limit=5)
    for artist in top_artists['items']:
        artist_id = artist['id']
        artist_name = artist['name']
        artist_genres = artist['genres']
        artist_top_tracks = spotify.artist_top_tracks(artist_id)
        related_artists = spotify.artist_related_artists(artist_id)
        #TODO recommended_tracks = spotify.recommendations(seed_artists=[artist_id], seed_genres=artist_genres)

        # Don't add duplicates
        playlist_name = artist_name + " vibes"
        playlists = spotify.current_user_playlists()
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                return
    
        playlist = spotify.user_playlist_create(user=user, name=playlist_name, public=False)
        track_uris = [track['uri'] for track in artist_top_tracks['tracks'][:5]]

        # your most played artist songs
        all_saved_songs = get_all_saved_songs()
        your_artist_songs = [track['track'] for track in all_saved_songs if any(artist_name == artist['name'] for artist in track['track']['artists'])]
        track_uris.extend([track['uri'] for track in your_artist_songs][:10])

        # add some songs from related artists
        for related_artist in related_artists['artists']:
            related_artist_top_tracks = spotify.artist_top_tracks(related_artist['id'])
            track_uris.extend([track['uri'] for track in related_artist_top_tracks['tracks']][:1])
        # add some songs from same genre
        for genre in artist_genres:
            genre_tracks = spotify.search(q='genre:' + genre, type='track', limit=1)    
            track_uris.extend([track['uri'] for track in genre_tracks['tracks']['items']])
        spotify.playlist_add_items(playlist_id=playlist['id'], items=track_uris)

        print(artist_name + ' vibes made')


#spotify.audio_features(track_uris)) TODO complexity algo
#results = sp.search(q=artist_name + 'Radio', type='playlist', limit=1) TODO radio songs 
'''
if __name__ == "__main__":
    app.run(debug=True)
