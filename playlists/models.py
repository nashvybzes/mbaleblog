from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='artists/' )
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    cover_image = models.ImageField(upload_to='song_covers/')
    rank = models.PositiveIntegerField(unique=True)
    is_bonus = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return f"{self.title} by {self.artist.name}"

class Playlist(models.Model):
    title = models.CharField(max_length=200, default="East Music Chart")
    songs = models.ManyToManyField(Song, related_name='playlists')
    top_song = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_playlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_songs(self):
        return Song.objects.filter(is_bonus=False).order_by('rank')

    def get_bonus_tracks(self):
        return Song.objects.filter(is_bonus=True).order_by('rank')