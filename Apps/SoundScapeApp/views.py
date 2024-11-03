from allauth.account.views import LoginView, SignupView
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
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
        return None


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
    access_token = social_account.socialtoken_set.first().token  # Get the access token
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    time_range = request.GET.get('time_range', 'medium_term')

    response = requests.get('https://api.spotify.com/v1/me/top/tracks?time_range=' + time_range, headers=headers)
    print(response.json())
    if response.status_code == 401:  # Token expired
        # Get Spotify app credentials from Allauth
        refresh_token = social_token.token_secret
        social_app = SocialApp.objects.get(provider='spotify')
        client_id = social_app.client_id
        client_secret = social_app.secret

        # Refresh the token
        sp_oauth = SpotifyOAuth(client_id,
                                client_secret,
                                redirect_uri='http://127.0.0.1:8000/accounts/spotify/login/callback/',
                                scope='user-top-read')

        new_token_info = sp_oauth.refresh_access_token(refresh_token)

        # Update the social token in the database
        social_token.token = new_token_info['access_token']
        social_token.save()

        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get('https://api.spotify.com/v1/me/top/artists?time_range=' + time_range, headers=headers)

    if response.status_code == 200:
        return render(request, 'SpotifyUserData.html', {'tracks': response.json()['items'],  'time_range': time_range})
    # Return the user's top tracks data
    else:
        # Handle error response
        return None

@login_required
def top_artists(request):
    social_account = SocialAccount.objects.get(user=request.user, provider='spotify')
    # Attempt to retrieve the associated token
    social_token = SocialToken.objects.filter(account=social_account).first()
    access_token = social_account.socialtoken_set.first().token  # Get the access token
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    time_range = request.GET.get('time_range', 'medium_term')

    response = requests.get('https://api.spotify.com/v1/me/top/artists?time_range=' + time_range, headers=headers)

    if response.status_code == 401:  # Token expired
        # Get Spotify app credentials from Allauth
        refresh_token = social_token.token_secret
        social_app = SocialApp.objects.get(provider='spotify')
        client_id = social_app.client_id
        client_secret = social_app.secret

        # Refresh the token
        sp_oauth = SpotifyOAuth(client_id,
                                client_secret,
                                redirect_uri='http://127.0.0.1:8000/accounts/spotify/login/callback/',
                                scope='user-top-read')

        new_token_info = sp_oauth.refresh_access_token(refresh_token)

        # Update the social token in the database
        social_token.token = new_token_info['access_token']
        social_token.save()

        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get('https://api.spotify.com/v1/me/top/artists?time_range=' + time_range, headers=headers)

    if response.status_code == 200:
        return render(request, 'UsersTopArtists.html', {'top_artists': response.json()['items'],  'time_range': time_range})
    # Return the user's top tracks data
    else:
        # Handle error response
        return None

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