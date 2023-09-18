from django.urls import path
from .views import *

urlpatterns = [
    path('get-auth-url', AuthURL.as_view()),
    path('redirect', spotify_callback),
    path('is-authenticated', IsAuthenticated.as_view()),
    path('current-song', CurrentSong.as_view()),
    path('pause', PauseSong.as_view()),
    path('play', PlaySong.as_view()),
    path('skip', SkipSong.as_view()),
    path('top-tracks-playlist', GenerateTopTracksPlaylist.as_view()),
    path('top-artist-playlist', GenerateTopArtistPlaylist.as_view()),
    path('top-artists', TopArtists.as_view()),
    path('update-playlist', UpdatePlaylist.as_view()),
]
