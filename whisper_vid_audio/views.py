from django.shortcuts import render
from .forms import TranscriptionForm
from .models import Transcription
from .transcribe import WhisperTranscriber
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

def upload_media(request):
    if request.method == 'POST':
        if 'media_file' in request.FILES:
            form = TranscriptionForm(request.POST, request.FILES)
            if form.is_valid():
                transcription = form.save()
                transcriber = WhisperTranscriber()
                result = transcriber.transcribe(transcription.media_file.path)
                transcription.transcribed_text = result['text']
                transcription.save()
                return render(request, 'whisper_vid_audio/result.html', {'transcription': transcription})
            else:
                logger.error(f"Form errors: {form.errors}")
        elif 'recorded_video' in request.FILES:
            video_data = request.FILES['recorded_video'].read()
            transcription = Transcription()
            transcription.media_file.save(f"recorded_{request.FILES['recorded_video'].name}", ContentFile(video_data))
            transcriber = WhisperTranscriber()
            result = transcriber.transcribe(transcription.media_file.path)
            transcription.transcribed_text = result['text']
            transcription.save()
            return render(request, 'whisper_vid_audio/result.html', {'transcription': transcription})
    else:
        form = TranscriptionForm()
    return render(request, 'whisper_vid_audio/upload.html', {'form': form})