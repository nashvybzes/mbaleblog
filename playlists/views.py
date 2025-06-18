from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Playlist, Song

def playlist_detail(request):
    playlist = get_object_or_404(Playlist, pk=1)  # Assuming you have one main playlist
    songs = playlist.get_songs()
    bonus_tracks = playlist.get_bonus_tracks()
    
    context = {
        'playlist': playlist,
        'songs': songs,
        'bonus_tracks': bonus_tracks,
        'is_admin': request.user.is_staff,
    }
    return render(request, 'playlists/playlist_detail.html', context)