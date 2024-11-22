from django.contrib.auth.decorators import login_required
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from urllib.parse import urlencode
import requests
from datetime import datetime, timedelta
from django.core.cache import cache

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
    access_token = SpotifyToken.objects.get(user=request.user).access_token
    print("yo", request.user, access_token)

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    time_range = request.GET.get('time_range', 'medium_term')

    response = requests.get('https://api.spotify.com/v1/me/top/tracks?time_range=' + time_range, headers=headers)
    print(response.content)

    if response.status_code == 401:  # Token expired
        print("Token expired")
        spotify_login(request, status='Expired')
        response = requests.get('https://api.spotify.com/v1/me/top/tracks?time_range=' + time_range, headers=headers)

    if response.status_code == 200:
        return render(request, 'SpotifyUserData.html', {'tracks': response.json()['items'],  'time_range': time_range})
    # Return the user's top tracks data
    else:
        # Handle error response
        return None

@login_required
def top_artists(request):
    access_token = SpotifyToken.objects.get(user=request.user).access_token
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    time_range = request.GET.get('time_range', 'medium_term')

    response = requests.get('https://api.spotify.com/v1/me/top/artists?time_range=' + time_range, headers=headers)

    if response.status_code == 401:  # Token expired
        print("Token expired")
        spotify_login(request, status='Expired')
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
    access_token = SpotifyToken.objects.get(user=request.user).access_token
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

def spotify_login(request, status=None):
    print("before setting", request.user)

    cache.set('User', request.user, timeout=60*15)  # Cache for 15 minutes

    if status == 'Expired':
        token = SpotifyToken.objects.get(user=request.user)
        refresh_url = "https://accounts.spotify.com/api/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        }

        response = requests.post(refresh_url, data=payload)
        data = response.json()

        if "access_token" in data:
            # Update the token and expiry in the database
            token.access_token = data["access_token"]
            token.token_expiry = datetime.now() + timedelta(seconds=data.get("expires_in", 3600))
            token.save()
            return token.access_token
        else:

            print(f"Error refreshing token: {data.get('error_description', 'Unknown error')}")
            return None

    else:
        auth_url = "https://accounts.spotify.com/authorize"
        params = {
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "scope": "user-top-read",
        }
        return redirect(f"{auth_url}?{urlencode(params)}")

def spotify_callback(request):
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
    print("callback: ", response.content)
    token_data = response.json()

    if "access_token" in token_data:
        user = cache.get('User')  # Retrieve the user from
        print("hey: ",user)
        SpotifyToken.objects.update_or_create(
            user=user,
            defaults={
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token"),
                "token_expiry": datetime.now() + timedelta(
                    seconds=token_data["expires_in"]
                ),
            },
        )
        print("after setting", user)
        cache.delete('User')
        return redirect("index")
    return redirect("error")