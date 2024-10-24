from allauth.account.views import LoginView, SignupView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from django.shortcuts import redirect, render


# Create your views here.
@login_required
def index(request):
    return render(request, 'AppBase.html')

@login_required
def fetch_spotify_data(request):
    # Spotify API authorization
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET
    ))

    # Get the search query from the request, or default to an empty string
    query = request.GET.get('q', '')  # Use an empty string if no query is provided

    try:
        results = sp.search(q=query, limit=10)
        songs = results['tracks']['items']
    except Exception as e:
        songs = []
        print(f"Error fetching data from Spotify: {e}")


    # Pass the data to the template
    return render(request, 'SpotifyData.html', {
        'songs': songs,
        'query': query,  # Pass the query back to the template for the form
    })

# Spotify OAuth settings (Authorization Code Flow)
@login_required
def spotify_authenticate(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,  # Use the redirect URI you set in the dashboard
        scope="user-top-read"  # Adjust scope based on your app's needs
    )

    # Step 1: Get the authorization URL
    auth_url = sp_oauth.get_authorize_url()

    # Step 2: Redirect user to Spotify for authorization
    return redirect(auth_url)

# Callback view where Spotify will redirect the user after authentication
@login_required
def spotify_callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='user-top-read'
    )

    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)

    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Get the time range from the user's request (default to medium_term if none provided)
    time_range = request.GET.get('time_range', 'medium_term')  # Can be 'short_term', 'medium_term', 'long_term'

    # Fetch the user's top tracks with the selected time range
    top_tracks = sp.current_user_top_tracks(time_range=time_range, limit=10)['items']

    return render(request, 'SpotifyUserData.html', {'tracks': top_tracks, 'time_range': time_range})

@login_required
def top_artists(request):
    # Default time range (e.g., 'medium_term')
    time_range = request.GET.get('time_range', 'medium_term')

    # Fetch the user's top artists
    results = sp.current_user_top_artists(limit=20, time_range=time_range)

    # Extract artist details
    top_artists = []
    for artist in results['items']:
        top_artists.append({
            'name': artist['name'],
            'popularity': artist['popularity'],
            'genres': artist['genres'],
            'image_url': artist['images'][0]['url'] if artist['images'] else None,
        })

    return render(request, 'UsersTopArtists.html', {'top_artists': top_artists, 'time_range': time_range})

@login_required
def profile_view(request):
    return render(request, 'Profile.html', {'user': request.user})

class CustomLoginView(LoginView):
    template_name = 'account/login.html'  # Your custom login template
    success_url = reverse_lazy('index')  # Redirect after successful login


class CustomSignupView(SignupView):
    template_name = 'account/signup.html'  # Your custom signup template
    success_url = reverse_lazy('index')  # Redirect after successful signup


def home(request):
    return render(request, 'Home.html')