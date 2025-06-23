from django.urls import path
from . import views

urlpatterns = [
    path('playlist/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('current/', views.current_playlist, name='current_playlist'),
    path('poll/<int:poll_id>/', views.poll_detail, name='poll_detail'),
    path('poll/<int:poll_id>/vote/<int:song_id>/', views.vote, name='vote'),
    path('poll/create/', views.create_poll, name='create_poll'),
    path('poll/<int:poll_id>/finalize/', views.finalize_poll, name='finalize_poll'),
    path('playlist/<int:playlist_id>/export/<str:format>/', views.export_playlist, name='export_playlist'),
]