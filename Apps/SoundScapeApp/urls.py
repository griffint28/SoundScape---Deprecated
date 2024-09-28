from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('spotify/', views.fetch_spotify_data, name='fetch_spotify_data'),
]