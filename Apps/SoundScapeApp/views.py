from django.shortcuts import render
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings

# Create your views here.
def index(request):

    return render(request, 'AppBase.html')

def fetch_spotify_data(request):
    # Spotify API authorization
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET
    ))

    # Search for a specific song (can be dynamic later)
    query = request.GET.get('q', 'Imagine')  # Default to 'Imagine' if no query
    results = sp.search(q=query, limit=10)

    # Extract relevant song data
    songs = results['tracks']['items']

    # Pass the data to the template
    return render(request, 'SpotifyData.html', {'songs': songs, 'query': query})