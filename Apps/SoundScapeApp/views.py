from allauth.account.views import LoginView, SignupView
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from django.conf import settings
from django.shortcuts import render
import requests

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

@login_required
def top_tracks(request):
    social_account = SocialAccount.objects.get(user=request.user, provider='spotify')
    # Attempt to retrieve the associated token
    social_token = SocialToken.objects.filter(account=social_account).first()
    print(social_token)
    access_token = social_account.socialtoken_set.first().token  # Get the access token
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    print(request.GET.get('time_range', 'medium_term'))
    time_range = request.GET.get('time_range', 'medium_term')
    print(time_range)

    response = requests.get('https://api.spotify.com/v1/me/top/tracks?time_range=' + time_range, headers=headers)
    print(response.json())

    if response.status_code == 200:
        return render(request, 'SpotifyUserData.html', {'tracks': response.json()['items'],  'time_range': time_range})
    # Return the user's top tracks data
    else:
        # Handle error response
        return None

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