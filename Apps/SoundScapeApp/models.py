from django.contrib.auth.models import User
from django.db import models

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    release_year = models.IntegerField()
    duration = models.FloatField()  # in minutes
    play_count = models.IntegerField()

    def __str__(self):
        return self.title

class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_expiry = models.DateTimeField()