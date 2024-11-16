from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from django.contrib.auth.decorators import login_required
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import spotipy
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from urllib.parse import urlencode
import requests
import datetime

from Apps.SoundScapeApp.models import SpotifyToken


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
        response = requests.get('https://api.spotify.com/v1/me/top/tracks?time_range=' + time_range, headers=headers)

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

def home(request):
    return render(request, 'Home.html')

def recommendations(request):
    social_account = SocialAccount.objects.get(user=request.user, provider='spotify')
    # Attempt to retrieve the associated token
    social_token = SocialToken.objects.filter(account=social_account).first()
    access_token = social_account.socialtoken_set.first().token  # Get the access token
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    time_range = request.GET.get('time_range', 'medium_term')

    tracksResponse = requests.get('https://api.spotify.com/v1/me/top/tracks?time_range=' + time_range, headers=headers)
    artistsResponse = requests.get('https://api.spotify.com/v1/me/top/artists?time_range=' + time_range, headers=headers)

    tracksResponseIDs = []
    for track in tracksResponse.json()['items']:
        tracksResponseIDs.append(track['id'])


    artistsResponseIDs = []
    artistsGenres = []
    for artist in artistsResponse.json()['items']:
        artistsResponseIDs.append(artist['id'])
        artistsGenres.append(artist['genres'][0])

    seed_artists = artistsResponseIDs[0]
    seed_tracks = tracksResponseIDs[0]
    seed_genres = artistsGenres[0]

    response =requests.get('https://api.spotify.com/v1/recommendations?'
                           'seed_artists=' + seed_artists
                           + '&seed_genres=' + seed_genres
                           + '&seed_tracks=' + seed_tracks
                           + '&max_popularity=70', headers=headers)

    # print(tracksResponseIDs)
    # print(artistsResponseIDs)
    # print(artistsGenres)
    print(response.json())

    recTracks = []
    for recTrack in response.json()['tracks']:
        recTracks.append(recTrack['name'] + ' by ' + recTrack['artists'][0]['name'])

    return render(request, 'Recommendations.html', {'recTracks': response.json()['tracks']})

def spotify_login(request):
    auth_url = "https://accounts.spotify.com/authorize"
    print(settings.SPOTIFY_REDIRECT_URI)
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": "user-read-email",
    }
    return redirect(f"{auth_url}?{urlencode(params)}")

def spotify_callback(request):
    print("callback")
    code = request.GET.get("code")
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=payload)
    token_data = response.json()

    if "access_token" in token_data:
        user = request.user  # Assumes user is logged in via Allauth
        SpotifyToken.objects.update_or_create(
            user=user,
            defaults={
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token"),
                "token_expiry": datetime.datetime.now() + datetime.timedelta(
                    seconds=token_data["expires_in"]
                ),
            },
        )
        return redirect("index")
    return redirect("error")