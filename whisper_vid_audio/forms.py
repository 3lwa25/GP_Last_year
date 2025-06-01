from django import forms
from .models import Transcription

class TranscriptionForm(forms.ModelForm):
    class Meta:
        model = Transcription
        fields = ['media_file']