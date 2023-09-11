from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from requests import post
from django.conf import settings 

# Function to get user tokens by session ID
def get_user_tokens(session_id):
    # Query the SpotifyToken model to find tokens associated with the given session ID
    user_tokens = SpotifyToken.objects.filter(user=session_id)
    
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None

# Function to update or create user tokens
def update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens(session_id)
    expires_in = timezone.now() + timedelta(seconds=expires_in)
    
    # If tokens exist, update their fields with the new values
    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token',
            'refresh_token', 'expires_in', 'token_type'])
    else:
        # If tokens do not exist, create a new SpotifyToken instance
        tokens = SpotifyToken(user=session_id, access_token=access_token,
                              refresh_token=refresh_token, token_type=token_type, expires_in=expires_in)
        tokens.save()

def is_spotify_authenticated(session_id):
    tokens = get_user_tokens(session_id)
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(session_id)
        return True
        
    return False

def refresh_spotify_token(session_id):
    refresh_token = get_user_tokens(session_id).refresh_token
    # Refresh the access token
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    refresh_token = response.get('refresh_token')
    
    # Update the access token and save it
    update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token)
