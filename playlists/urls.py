from django.urls import path
from . import views

urlpatterns = [
    path('', views.playlist_detail, name='playlist_detail'),
]