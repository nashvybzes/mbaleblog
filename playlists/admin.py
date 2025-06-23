from django.contrib import admin
from .models import Artist, Song, Poll, PollSong, Vote, Playlist, PlaylistSong

class PollSongInline(admin.TabularInline):
    model = PollSong
    extra = 0

class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    inlines = [PollSongInline]
    
    actions = ['finalize_poll']
    
    def finalize_poll(self, request, queryset):
        for poll in queryset:
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
        
        self.message_user(request, f"Successfully finalized {queryset.count()} polls.")
    finalize_poll.short_description = "Finalize selected polls and generate playlists"

class PlaylistSongInline(admin.TabularInline):
    model = PlaylistSong
    extra = 0
    ordering = ('order',)

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('title',)
    inlines = [PlaylistSongInline]
    
    actions = ['set_as_current']
    
    def set_as_current(self, request, queryset):
        Playlist.objects.filter(is_current=True).update(is_current=False)
        queryset.update(is_current=True)
        self.message_user(request, f"Set {queryset.count()} playlists as current.")
    set_as_current.short_description = "Set selected playlists as current"

admin.site.register(Artist)
admin.site.register(Song)
admin.site.register(Poll, PollAdmin)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Vote)

admin.site.site_header = "Nash Vybzes™ Admin Dashboard" 
admin.site.site_title = "Nash Vybzes™ Admin"            
admin.site.index_title = "The Nash Vybzes™ Admin Portal"