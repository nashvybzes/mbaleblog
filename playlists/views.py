from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from blog.views import get_trending_posts
from .models import Playlist, Song


def playlist_detail(request):
    trending_posts = get_trending_posts()
    playlist = get_object_or_404(Playlist, pk=1)  
    songs = playlist.get_songs()
    bonus_tracks = playlist.get_bonus_tracks()
    
    context = {
        'trending_posts': trending_posts,
        'playlist': playlist,
        'songs': songs,
        'bonus_tracks': bonus_tracks,
        'is_admin': request.user.is_staff,
    }
    return render(request, 'playlists/playlist_detail.html', context)