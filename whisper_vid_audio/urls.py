from django.urls import path
from . import views

app_name = 'whisper_vid_audio'

urlpatterns = [
    path('', views.upload_media, name='upload'),
]