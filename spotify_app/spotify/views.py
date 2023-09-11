from django.shortcuts import render
from rest_framework.views import APIView
from requests import Request, post
from django.conf import settings 
from rest_framework.response import Response
from rest_framework import status
from .util import *
from django.shortcuts import redirect
from api.models import Room

# Define a class for handling Spotify authentication URL generation
class AuthURL(APIView):
    def get(self, request, format=None):
        # Define the desired Spotify API scopes for authorization
        scopes = 'user-library-read playlist-modify-public playlist-modify-private user-top-read user-read-recently-played playlist-read-private playlist-read-collaborative user-read-playback-state user-modify-playback-state user-read-currently-playing'
        
        # Generate the Spotify authorization URL
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': settings.REDIRECT_URI,
            'client_id': settings.CLIENT_ID
        }).prepare().url

        # Return the generated URL as a response
        return Response({'url': url}, status=status.HTTP_200_OK)

# Define a callback function for handling Spotify authorization callback
def spotify_callback(request, format=None):
    # Retrieve the authorization code and error (if any) from the callback URL parameters
    code = request.GET.get('code')

    # Send a POST request to Spotify to exchange the authorization code for access tokens
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.REDIRECT_URI,
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET
    }).json()

    # Extract relevant information from the response
    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')

    # Create a session if it doesn't exist
    if not request.session.exists(request.session.session_key):
        request.session.create()

    # Update or create user tokens in the session
    update_or_create_user_tokens(
        request.session.session_key, access_token, token_type, expires_in, refresh_token)

    # Redirect to the frontend (assuming a URL pattern named 'frontend:' exists)
    return redirect('frontend:')

class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)
    
class CurrentSong(APIView):
    def get(self, request, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        host = room.host
        endpoint = "player/currently-playing"
        response = execute_spotify_api_request(host, endpoint)

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
            
        song = {
            'title': item.get('name'),
            'artist': artist_string,
            'duration': duration,
            'time': progress,
            'image_url': album_cover,
            'is_playing': is_playing,
            'votes': 0,
            'id': song_id
        }

        return Response(song, status=status.HTTP_200_OK)