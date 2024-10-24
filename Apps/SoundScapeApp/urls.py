from django.urls import path
from . import views
from .views import CustomLoginView, CustomSignupView

urlpatterns = [
    path('index/', views.index, name='index'),
    path('spotify/', views.fetch_spotify_data, name='fetch_spotify_data'),
    path('spotify-login/', views.spotify_authenticate, name='spotify_authenticate'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('top-artists/', views.top_artists, name='top_artists'),
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
    path('accounts/profile/', views.profile_view, name='profile_view'),
    path('', views.home, name='home')
]