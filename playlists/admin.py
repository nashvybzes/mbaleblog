from django.contrib import admin
from .models import Artist, Song, Playlist


class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'top_song', 'created_at' )
    filter_horizontal = ('songs',)

admin.site.register(Artist)
admin.site.register(Song)
admin.site.register(Playlist, PlaylistAdmin)

admin.site.site_header = "Nash Vybzes™ Admin Dashboard" 
admin.site.site_title = "Nash Vybzes™ Admin"            
admin.site.index_title = "The Nash Vybzes™ Admin Portal"