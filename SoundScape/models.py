from django.db import models

class MusicFile(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='music/')