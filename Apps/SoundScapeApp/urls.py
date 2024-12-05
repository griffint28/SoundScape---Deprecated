from django.urls import path
from . import views

urlpatterns = [
    #paths that don't require a user to be logged in
    path('', views.home, name='home'),

    #paths that require a user to be logged in
    path('index/', views.index, name='index'),
    path('accounts/profile/', views.profile_view, name='profile_view'),
    path('top-tracks/', views.top_tracks, name='top_tracks'),
    path('top-artists/', views.top_artists, name='top_artists'),

    #process for logining spotify
    path('spotify-login/', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
]