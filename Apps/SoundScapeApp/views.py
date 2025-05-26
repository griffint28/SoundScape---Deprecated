from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from urllib.parse import urlencode
import requests
from datetime import datetime, timedelta
from django.core.cache import cache

from Apps.SoundScapeApp.helper import generate_jokes
from Apps.SoundScapeApp.models import SpotifyToken

#TODO: Helper functions for obtaining user's top tracks, top artists, and recommendations
#TODO: Change scope to allow for recommendations to be saved to user's spotify account
#TODO: Add error handling for end user, make it where all errors are displayed for development
#TODO: Add centralized CSS file for all pages

def home(request):
    return render(request, 'Home.html')

@login_required
def index(request):
    return render(request, 'Index.html')

@login_required
def profile_view(request):
    return render(request, 'Profile.html', {'user': request.user})

@login_required
def top_tracks(request):
    #TODO: Add error handling for when user is not in token table
    #TODO: Add better error handling for when token is expired
    #TODO: Add error response for end user
    #TODO: Add CSS for layout of top tracks
    #TODO: Consistent for time range change (Be like top artists)

    #obtain the user's access token
    access_token = SpotifyToken.objects.get(user=request.user).access_token

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    time_range = request.GET.get('time_range', 'medium_term')

    response = requests.get('https://api.spotify.com/v1/me/top/tracks?time_range=' + time_range, headers=headers)

    if response.status_code == 200:
        cache.set('top_tracks', response.json()['items'][:5], timeout=60*15)  #Grab top 5, cache for 15 minutes
        return render(request, 'UsersTopTracks.html', {'tracks': response.json()['items'], 'time_range': time_range})
    elif response.status_code == 401:
        print("Token expired, refreshing")
        spotify_login(request, status='Expired')
        access_token = SpotifyToken.objects.get(user=request.user).access_token
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get('https://api.spotify.com/v1/me/top/tracks?time_range=' + time_range, headers=headers)
        print(response.json())
        return render(request, 'UsersTopTracks.html', {'tracks': response.json()['items'], 'time_range': time_range})
    else:
        return None

@login_required
def top_artists(request):
    #TODO: Add error handling for when user is not in token table
    #TODO: Add better error handling for when token is expired
    #TODO: Add error response for end user
    #TODO: Add CSS for layout of top artists

    access_token = SpotifyToken.objects.get(user=request.user).access_token
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    time_range = request.GET.get('time_range', 'medium_term')

    response = requests.get('https://api.spotify.com/v1/me/top/artists?time_range=' + time_range, headers=headers)

    if response.status_code == 401:  # Token expired
        spotify_login(request, status='Expired')
        response = requests.get('https://api.spotify.com/v1/me/top/artists?time_range=' + time_range, headers=headers)

    if response.status_code == 200:
        cache.set('top_artists', response.json()['items'][:5], timeout=60*15)  # Grab top 5, cache for 15 minutes
        return render(request, 'UsersTopArtists.html', {'top_artists': response.json()['items'],  'time_range': time_range})
    # Return the user's top tracks data
    else:
        # Handle error response
        return None

@login_required
def jokes(request):
    top_tracks, top_artists = None, None
    if cache.get('top_artists') is None and cache.get('top_tracks') is None:
        access_token = SpotifyToken.objects.get(user=request.user).access_token

        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        time_range = request.GET.get('time_range', 'medium_term')

        top_tracks = requests.get('https://api.spotify.com/v1/me/top/tracks?time_range=' + time_range + 'limit=5', headers=headers)

        access_token = SpotifyToken.objects.get(user=request.user).access_token
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        time_range = request.GET.get('time_range', 'medium_term')

        top_artists = requests.get('https://api.spotify.com/v1/me/top/artists?time_range=' + time_range + 'limit=5', headers=headers)
    else:
        top_tracks = cache.get('top_tracks')
        top_artists = cache.get('top_artists')

    formattedTracks, formattedArtists = [], []
    for track in top_tracks:
        formattedTracks.append(str(dict(track)['name']) + " by " + str(dict(track)['artists'][0]['name']))
    print(top_artists)
    for artist in top_artists:
        formattedArtists.append(str(dict(artist)['name']))

    print(formattedTracks)
    print(formattedArtists)

    response = generate_jokes(formattedTracks, formattedArtists)
    print(response)
    return render(request, 'UsersJokes.html', context={'jokes': response})

def spotify_login(request, status=None):
    #TODO: Error handling for when user is not in token table

    #set cache for user so it can be retrieved after spotify login
    cache.set('User', request.user, timeout=60*15)  # Cache for 15 minutes

    #check if function was called due to token expiration
    if status == 'Expired':
        print("token expired, refreshing")

        #Obtain the user's token
        token = SpotifyToken.objects.get(user=request.user)

        #Base URL for refreshing token
        refresh_url = "https://accounts.spotify.com/api/token"

        #Assemble the payload for the POST request
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        }

        #Send the POST request
        response = requests.post(refresh_url, data=payload)

        #Parse the response
        data = response.json()

        #Check if the response contains an access token
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
        #Base URL for Spotify OAuth
        auth_url = "https://accounts.spotify.com/authorize"

        #Parameters for the OAuth request
        params = {
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "scope": "user-top-read",
        }

        #Redirect the user to the Spotify OAuth
        return redirect(f"{auth_url}?{urlencode(params)}")

def spotify_callback(request):
    #Obtain the code from the request
    code = request.GET.get("code")

    #Base URL for Spotify token request
    token_url = "https://accounts.spotify.com/api/token"

    #Assemble the payload for the POST request
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }

    #Send the POST request
    response = requests.post(token_url, data=payload)

    #Parse the response
    token_data = response.json()

    #Check if the response contains an access token
    if "access_token" in token_data:
        #Retrieve the user from the cache from the spotify_login function
        user = cache.get('User')

        #Update the user's token in the database
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

        #Clear cache and redirect the user to the index page
        cache.delete('User')
        #TODO: Local Dev vs Prod settings needed
        return redirect("http://localhost:5173/dashboard")

    return redirect("error")


def simple_data(request):
    return JsonResponse({
        "message": "Hello from Django!",
        "items": ["React", "Django", "testing"]
    })
