from rest_framework.views import APIView
from django.conf import settings 
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from api.models import Room
from .models import Vote
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

BASE_URL = 'https://api.spotify.com/v1/'

sp_oauth = SpotifyOAuth(    
    settings.CLIENT_ID,
    settings.CLIENT_SECRET,
    settings.REDIRECT_URI,
    scope='user-library-read playlist-modify-public playlist-modify-private user-top-read user-read-recently-played playlist-read-private playlist-read-collaborative user-read-playback-state user-modify-playback-state user-read-currently-playing'
)

#TODO change to cached?
def is_spotify_authenticated(request):
    try:
        token_info = request.get('token_info')
    except:
        token_info = request.session.get('token_info')

    #token_info = sp_oauth.cache_handler.get_cached_token()
    if token_info:
        if sp_oauth.is_token_expired(token_info):
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            sp_oauth.cache_handler.save_token_to_cache(token_info)
            try:
                request.session['token_info'] = token_info
            except:
                request['token_info'] = token_info
        return True
        
    return False

def validate(request):
    if is_spotify_authenticated(request):
        return spotipy.Spotify(auth=request.session['token_info']['access_token'])
    else:
        return Response({}, status=status.HTTP_401_UNAUTHORIZED)   

class AuthURL(APIView):
    def get(self):
        url = sp_oauth.get_authorize_url()
        return Response({'url': url}, status=status.HTTP_200_OK)

def spotify_callback(request):
    # Retrieve the authorization code and error (if any) from the callback URL parameters
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)

    if not request.session.exists(request.session.session_key):
        request.session.create()

    request.session['token_info'] = token_info

    return redirect('frontend:')

class IsAuthenticated(APIView):
    def get(self, request):
        is_authenticated = is_spotify_authenticated(request.session)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)
    
class CurrentSong(APIView):
    def get(self, request):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        
        response = validate(request).current_user_playing_track()

        if not response or 'error' in response or 'item' not in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        item = response.get('item')
        duration = item.get('duration_ms')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('images')[0].get('url')
        is_playing = response.get('is_playing')
        song_id = item.get('id')

        artist_string = ""

        for i, artist in enumerate(item.get('artists')):
            if i > 0:
                artist_string += ", "
            name = artist.get('name')
            artist_string += name
            
        votes = Vote.objects.filter(room=room, song_id=song_id).count()

        song = {
            'title': item.get('name'),
            'artist': artist_string,
            'duration': duration,
            'time': progress,
            'image_url': album_cover,
            'is_playing': is_playing,
            'votes': votes,
            'votes_required': room.votes_to_skip,
            'id': song_id
        }

        self.update_room_song(room, song_id)
        return Response(song, status=status.HTTP_200_OK)
    
    def update_room_song(self, room, song_id):
        current_song = room.current_song
        if current_song != song_id:
            room.current_song = song_id
            room.save(update_fields=['current_song'])
            Vote.objects.filter(room=room).delete()
    
class PauseSong(APIView):
    def put(self, request):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code).first()
        if self.request.session.session_key == room.host or room.guest_can_pause:
            validate(request).pause_playback()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({}, status=status.HTTP_403_FORBIDDEN)
    
class PlaySong(APIView):
    def put(self, request):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code).first()
        if self.request.session.session_key == room.host or room.guest_can_pause:
            validate(request).start_playback()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({}, status=status.HTTP_403_FORBIDDEN)
    
class SkipSong(APIView):
    def post(self, request):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code).first()
        votes = Vote.objects.filter(room=room, song_id=room.current_song)
        votes_needed = room.votes_to_skip

        if self.request.session.session_key == room.host or len(votes) + 1 >= votes_needed:
            votes.delete()
            validate(request).next_track()
        else:
            vote = Vote(user=self.request.session.session_key, room=room, song_id=room.current_song)
            vote.save()
        
        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
class GenerateTopTracksPlaylist(APIView):
    def put(self, request):
        time_range = request.data.get('time_range')
        sp = validate(request)
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
        
        return Response({}, status=status.HTTP_200_OK)

class GenerateTopArtistPlaylist(APIView):
    def put(self, request):
        sp = validate(request)
        artist_id = request.data.get('artist_id')

        artist = sp.artist(artist_id)
        artist_name = artist['name']
        artist_genres = artist['genres']
        artist_top_tracks = sp.artist_top_tracks(artist_id)
        related_artists = sp.artist_related_artists(artist_id)

        playlist_name = artist_name + " Vibes"
        playlists = sp.current_user_playlists()
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                sp.current_user_unfollow_playlist(playlist['id'])
            
        # Create playlist
        playlist = sp.user_playlist_create(user=sp.current_user()['id'], name=playlist_name, public=False)
        track_uris = [track['uri'] for track in artist_top_tracks['tracks'][:5]]


        def get_all_saved_songs():
            offset = 0
            all_saved_tracks = []
            while True:
                saved_tracks = sp.current_user_saved_tracks(limit=50, offset=offset)
                if not saved_tracks['items']:
                    break  # No more tracks to retrieve
                all_saved_tracks.extend(saved_tracks['items'])
                offset += 50
            return all_saved_tracks


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
        
        return Response({}, status=status.HTTP_200_OK)

class TopArtists(APIView):
    def get(self, request):
        sp = validate(request)
        top_artists = sp.current_user_top_artists(time_range='long_term', limit=10)['items']
        top_artist_data = [{'id': artist['id'], 'name': artist['name']} for artist in top_artists]
        return Response(top_artist_data, status=status.HTTP_200_OK)
    
class UpdatePlaylist(APIView):
    def put(self, request, format=None):
        sp = validate(request)
        try:
            artist_id = request.data.get('artist_id')
            artist = sp.artist(artist_id)
            artist_name = artist['name']
            playlist_name = artist_name + " Vibes"
        except:
            time_range = request.data.get('time_range')
            if time_range == 'short_term': playlist_name = "Recently listened vibes"
            elif time_range == 'medium_term': playlist_name = "Throwback tracks"
            else: playlist_name = "All time favourites"

        playlists = sp.current_user_playlists()
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                return Response(playlist_name, status=status.HTTP_200_OK)
        
        return Response({}, status=status.HTTP_404_NOT_FOUND)
        
