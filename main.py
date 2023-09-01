import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import config

scope = 'user-library-read playlist-modify-public playlist-modify-private user-top-read user-read-recently-played playlist-read-private playlist-read-collaborative'

def getToken():
    # Get access token
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config.client_id,client_secret=config.client_secret,redirect_uri=config.redirect_uri,scope=scope))

def createTopPlaylist(time_range):
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
            return
        
    # TODO recommended_tracks = spotify.recommendations(seed_tracks=track_uris)
    playlist = spotify.user_playlist_create(user=user, name=playlist_name, public=False)
    track_uris = [track['uri'] for track in tracks['items']]
    spotify.playlist_add_items(playlist_id=playlist['id'], items=track_uris)

    print(playlist_name + ' made')

def getAllSavedSongs():
    offset = 0
    all_saved_tracks = []
    while True:
        saved_tracks = spotify.current_user_saved_tracks(limit=50, offset=offset)
        if not saved_tracks['items']:
            break  # No more tracks to retrieve
        all_saved_tracks.extend(saved_tracks['items'])
        offset += 50
    return all_saved_tracks

def creatArtistPlaylist():
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
        all_saved_songs = getAllSavedSongs()
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
 
if __name__ == "__main__":
    spotify = getToken()
    user = spotify.current_user()['id']
    for time_range in ['short_term', 'medium_term', 'long_term']:
        createTopPlaylist(time_range)
    creatArtistPlaylist()
    print('program end')
