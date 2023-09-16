from django.shortcuts import render
from rest_framework.views import APIView
from requests import Request, post
from django.conf import settings 
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from api.models import Room
from .models import Vote
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import session

BASE_URL = 'https://api.spotify.com/v1/'

sp_oauth = SpotifyOAuth(    
    settings.CLIENT_ID,
    settings.CLIENT_SECRET,
    settings.REDIRECT_URI,
    scope='user-library-read playlist-modify-public playlist-modify-private user-top-read user-read-recently-played playlist-read-private playlist-read-collaborative user-read-playback-state user-modify-playback-state user-read-currently-playing'
)

def is_spotify_authenticated(request):
    token_info = request.session.get('token_info')
    if token_info:
        if sp_oauth.is_token_expired(token_info):
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            sp_oauth.cache_handler.save_token_to_cache(token_info)
            request.session['token_info'] = token_info
        return True
        
    return False

def validate(request):
    if is_spotify_authenticated(request):
        return spotipy.Spotify(auth=request.session['token_info']['access_token'])
    else:
        return Response({}, status=status.HTTP_401_UNAUTHORIZED)   

class AuthURL(APIView):
    def get(self, request, format=None):
        url = sp_oauth.get_authorize_url()
        return Response({'url': url}, status=status.HTTP_200_OK)

def spotify_callback(request, format=None):
    # Retrieve the authorization code and error (if any) from the callback URL parameters
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)

    if not request.session.exists(request.session.session_key):
        request.session.create()

    request.session['token_info'] = token_info

    return redirect('frontend:')

class IsAuthenticated(APIView):
    def get(self, request, format=None):
        print(request, 'REQUEST')
        print(request.session, 'SESSION')
        print(request.session.session_key, 'SESSION KEY')
        is_authenticated = is_spotify_authenticated(self.request.session)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)
    
class CurrentSong(APIView):
    def get(self, request, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        
        sp = validate(request)  
        response =  sp.current_user_playing_track()

        if 'error' in response or 'item' not in response:
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
    def put(self, request, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code).first()
        if self.request.session.session_key == room.host or room.guest_can_pause:
            validate(request).pause_playback()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({}, status=status.HTTP_403_FORBIDDEN)
    
class PlaySong(APIView):
    def put(self, request, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code).first()
        if self.request.session.session_key == room.host or room.guest_can_pause:
            validate(request).start_playback()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({}, status=status.HTTP_403_FORBIDDEN)
    
class SkipSong(APIView):
    def post(self, request, format=None):
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
    