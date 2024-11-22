from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('top-artists/', views.top_artists, name='top_artists'),
    path('top-tracks/', views.top_tracks, name='top_tracks'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('accounts/profile/', views.profile_view, name='profile_view'),
    path('', views.home, name='home'),
    path('spotify-login/', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
]