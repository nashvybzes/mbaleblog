from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.cache import cache
from .models import Poll, PollSong, Vote, Playlist, Song, Artist
from .forms import PollForm, SongSelectionForm
import json
from urllib.parse import urlparse
from ipware import get_client_ip
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token

@require_POST
@ensure_csrf_cookie
def vote(request, poll_id, song_id):
    try:
        # Verify poll exists and is active
        poll = get_object_or_404(Poll, pk=poll_id)
        if not poll.is_active:
            return JsonResponse({
                'status': 'error',
                'message': 'This poll is not active.',
                'csrf_token': get_token(request)
            }, status=400)

        # Verify song exists in this poll
        poll_song = get_object_or_404(PollSong, pk=song_id, poll=poll)

        # Get client IP and session
        client_ip, _ = get_client_ip(request)
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        # Check for existing votes
        if (Vote.objects.filter(poll=poll, ip_address=client_ip).exists() or
            (session_key and Vote.objects.filter(poll=poll, session_key=session_key).exists())):
            return JsonResponse({
                'status': 'error',
                'message': 'You have already voted in this poll.',
                'csrf_token': get_token(request)
            }, status=400)

        # Record the vote
        Vote.objects.create(
            poll=poll,
            song=poll_song,
            ip_address=client_ip,
            session_key=session_key
        )

        # Update vote count
        poll_song.votes += 1
        poll_song.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Vote recorded!',
            'csrf_token': get_token(request)
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'csrf_token': get_token(request)
        }, status=500)

def is_staff(user):
    return user.is_staff

def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    
    context = {
        'playlist': playlist,
        'songs': playlist.songs,
        'is_admin': request.user.is_staff,
    }
    
    # Add bonus tracks if they exist
    if playlist.bonus_tracks.exists():
        context['bonus_tracks'] = [ps.song for ps in playlist.bonus_tracks]
    
    return render(request, 'playlists/playlist.html', context)

def current_playlist(request):
    playlist = Playlist.objects.filter(is_current=True).first()
    if not playlist:
        return render(request, 'playlists/no_playlist.html')
    return playlist_detail(request, playlist.id)

def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    poll_songs = poll.pollsong_set.all().order_by('-votes')
    total_votes = sum(ps.votes for ps in poll_songs)
    
    # Calculate percentages
    for song in poll_songs:
        song.percentage = (song.votes / total_votes * 100) if total_votes > 0 else 0
    
    # Check if user has already voted
    has_voted = False
    if not request.user.is_authenticated:
        client_ip, _ = get_client_ip(request)
        session_key = request.session.session_key
        if Vote.objects.filter(poll=poll, ip_address=client_ip).exists() or \
           (session_key and Vote.objects.filter(poll=poll, session_key=session_key).exists()):
            has_voted = True
    
    context = {
        'poll': poll,
        'poll_songs': poll_songs,
        'total_votes': total_votes,
        'has_voted': has_voted,
        'is_admin': request.user.is_staff,
    }
    
    return render(request, 'playlists/poll.html', context)

@login_required
@user_passes_test(is_staff)
def create_poll(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.save()
            
            # Add selected songs to poll
            selected_songs = form.cleaned_data['songs']
            for song in selected_songs:
                PollSong.objects.create(poll=poll, song=song)
            
            return redirect('poll_detail', poll_id=poll.id)
    else:
        form = PollForm()
    
    return render(request, 'playlists/create_poll.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def finalize_poll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    
    if poll.is_active:
        return JsonResponse({'status': 'error', 'message': 'Poll is still active.'}, status=400)
    
    # Get ranked songs by votes
    poll_songs = poll.pollsong_set.all().order_by('-votes')
    
    # Assign ranks
    for rank, poll_song in enumerate(poll_songs, start=1):
        poll_song.rank = rank
        poll_song.save()
    
    # Create or update playlist
    playlist, created = Playlist.objects.get_or_create(
        poll=poll,
        defaults={'title': f'Top Songs from {poll.title}'}
    )
    
    if not created:
        playlist.title = f'Top Songs from {poll.title}'
        playlist.save()
    
    # Update playlist from poll results
    playlist.update_from_poll(poll)
    
    # Set this as current playlist
    Playlist.objects.filter(is_current=True).update(is_current=False)
    playlist.is_current = True
    playlist.save()
    
    return JsonResponse({'status': 'success', 'message': 'Playlist generated successfully!'})

@login_required
@user_passes_test(is_staff)
def export_playlist(request, playlist_id, format):
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    
    if format not in ['png', 'webp', 'svg']:
        return HttpResponseForbidden("Invalid export format")
    
    # In a real implementation, you would generate the image here
    # For now, we'll just return a JSON response
    return JsonResponse({
        'status': 'success',
        'message': f'Playlist exported as {format}',
        'download_url': f'/media/exports/playlist_{playlist_id}.{format}'
    })