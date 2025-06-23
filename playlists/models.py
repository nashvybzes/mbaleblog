from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Artist(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='artists/',default='images/logo.png',blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    cover_image = models.ImageField(upload_to='song_covers/', default='images/logo.png')
    
    def __str__(self):
        return f"{self.title} - {self.artist.name}"

class Poll(models.Model):
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    songs = models.ManyToManyField(Song, through='PollSong')
    
    def save(self, *args, **kwargs):
        now = timezone.now()
        if self.start_time <= now <= self.end_time:
            self.is_active = True
        else:
            self.is_active = False
        super().save(*args, **kwargs)
    
    def update_status(self):
        now = timezone.now()
        if self.start_time <= now <= self.end_time:
            self.is_active = True
        else:
            self.is_active = False
        self.save()
    
    def __str__(self):
        return self.title

class PollSong(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    votes = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-votes']
    
    def __str__(self):
        return f"{self.song.title} in {self.poll.title} - Votes: {self.votes}"

class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    song = models.ForeignKey(PollSong, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=45)
    session_key = models.CharField(max_length=40)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['poll', 'ip_address'], ['poll', 'session_key']]
    
    def __str__(self):
        return f"Vote for {self.song.song.title} from {self.ip_address}"

class Playlist(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    poll = models.OneToOneField(Poll, on_delete=models.SET_NULL, null=True, blank=True)
    is_current = models.BooleanField(default=False)
    
    def update_from_poll(self, poll):
        # Clear existing songs
        self.playlist_songs.all().delete()
        
        # Get ranked songs from poll
        poll_songs = poll.pollsong_set.filter(rank__isnull=False).order_by('rank')
        
        # Add songs to playlist
        for order, poll_song in enumerate(poll_songs, start=1):
            PlaylistSong.objects.create(
                playlist=self,
                song=poll_song.song,
                order=order
            )
        
        # Set top song
        if poll_songs.exists():
            self.top_song = poll_songs.first().song
            self.save()
    
    @property
    def top_song(self):
        return self.playlist_songs.first().song if self.playlist_songs.exists() else None
    
    @property
    def songs(self):
        return [ps.song for ps in self.playlist_songs.order_by('order')]
    
    @property
    def bonus_tracks(self):
        return self.playlist_songs.filter(is_bonus=True).order_by('order')
    
    def __str__(self):
        return self.title

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='playlist_songs')
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    is_bonus = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
        unique_together = ['playlist', 'order']
    
    def __str__(self):
        return f"{self.order}. {self.song.title} in {self.playlist.title}"