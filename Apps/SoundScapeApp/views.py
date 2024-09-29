from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from django.shortcuts import redirect, render


# Create your views here.
def index(request):
    return render(request, 'AppBase.html')

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
def spotify_authenticate(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,  # Use the redirect URI you set in the dashboard
        scope="user-library-read playlist-read-private"  # Adjust scope based on your app's needs
    )

    # Step 1: Get the authorization URL
    auth_url = sp_oauth.get_authorize_url()

    # Step 2: Redirect user to Spotify for authorization
    return redirect(auth_url)

# Callback view where Spotify will redirect the user after authentication
def spotify_callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-library-read playlist-read-private"
    )

    # Step 3: Spotify redirects back to this callback URL with a code in the query parameters
    code = request.GET.get('code')

    # Step 4: Exchange code for access token
    token_info = sp_oauth.get_access_token(code)

    if token_info:
        access_token = token_info['access_token']

        # Step 5: Use the access token to make requests to Spotify on behalf of the user
        sp = spotipy.Spotify(auth=access_token)
        user_data = sp.current_user()
        saved_tracks = sp.current_user_saved_tracks(limit=10)

        return render(request, 'SpotifyUserData.html', {'user': user_data, 'tracks': saved_tracks})
    else:
        return render(request, 'Error.html', {'message': 'Authentication failed'})
