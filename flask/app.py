import spotipy, time, random, config
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect, render_template

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'spotify-session'
app.secret_key = 'palylist-generator-secret'

@app.route('/')
def login():
    return redirect(create_spotify_oauth().get_authorize_url())

@app.route('/home')
def home():
    if 'token_info' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/redirect')
def redirect_page():
    session.clear()
    session['token_info'] = create_spotify_oauth().get_access_token(request.args.get('code'))
    return redirect(url_for('home'))

@app.route('/createTopTracksPlaylists')
def create_top_tracks_playlists():
    sp = validate()
    for time_range in ['short_term', 'medium_term', 'long_term']:
        tracks = sp.current_user_top_tracks(time_range=time_range, limit=50)
        if time_range == 'short_term': playlist_name = "Recently listened vibes"
        elif time_range == 'medium_term': playlist_name = "Throwback tracks"
        else: playlist_name = "All time favourites"
        playlists = sp.current_user_playlists()

        # Remove playlist
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                sp.current_user_unfollow_playlist(playlist['id'])
            
        # TODO recommended_tracks = spotify.recommendations(seed_tracks=track_uris)
        # Create playlist
        playlist = sp.user_playlist_create(user=sp.current_user()['id'], name=playlist_name, public=False)
        track_uris = [track['uri'] for track in tracks['items']]
        sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
    return render_template('success.html', name='top tracks playlists made')

@app.route('/createTopArtistsPlaylists')
def create_top_artists_playlists():
    sp = validate()
    top_artists = sp.current_user_top_artists(time_range='long_term', limit=10)['items']
    return render_template('top_artists.html', top_artists=top_artists)

@app.route('/createTopArtistPlaylist/<artist_id>')
def create_top_artist_playlist(artist_id):
    sp = validate()
    artist = sp.artist(artist_id)
    artist_name = artist['name']
    artist_genres = artist['genres']
    artist_top_tracks = sp.artist_top_tracks(artist_id)
    related_artists = sp.artist_related_artists(artist_id)
    #TODO recommended_tracks = spotify.recommendations(seed_artists=[artist_id], seed_genres=artist_genres)

    # Remove playlist
    playlist_name = artist_name + " Vibes"
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            sp.current_user_unfollow_playlist(playlist['id'])

    # Create playlist
    playlist = sp.user_playlist_create(user=sp.current_user()['id'], name=playlist_name, public=False)
    track_uris = [track['uri'] for track in artist_top_tracks['tracks'][:5]]

    # your most played artist songs
    all_saved_songs = get_all_saved_songs()
    your_artist_songs = [track['track'] for track in all_saved_songs if any(artist_name == artist['name'] for artist in track['track']['artists'])]
    track_uris.extend([track['uri'] for track in your_artist_songs][:10])

    # add some songs from related artists
    for related_artist in related_artists['artists']:
        related_artist_top_tracks = sp.artist_top_tracks(related_artist['id'])
        track_uris.extend([track['uri'] for track in related_artist_top_tracks['tracks']][:1])
    # add some songs from same genre
    for genre in artist_genres:
        genre_tracks = sp.search(q='genre:' + genre, type='track', limit=1)    
        track_uris.extend([track['uri'] for track in genre_tracks['tracks']['items']])
    sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
    # add some songs from artist radio
    radio = sp.search(q=artist_name + ' Radio', type='playlist', limit=1)
    radio_tracks = sp.playlist_items(radio['playlists']['items'][0]['id'])
    random.shuffle(radio_tracks['items'])
    track_uris.extend([track['track']['uri'] for track in radio_tracks['items']][:5])
    
    return render_template('success.html', name=playlist_name + ' made')

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

def get_all_saved_songs():
    sp = validate()
    offset = 0
    all_saved_tracks = []
    while True:
        saved_tracks = sp.current_user_saved_tracks(limit=50, offset=offset)
        if not saved_tracks['items']:
            break  # No more tracks to retrieve
        all_saved_tracks.extend(saved_tracks['items'])
        offset += 50
    return all_saved_tracks

if __name__ == "__main__":
    app.run(debug=True)