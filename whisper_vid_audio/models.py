from django.db import models

class Transcription(models.Model):
    media_file = models.FileField(upload_to='media/%Y/%m/%d/')
    transcribed_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transcription {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"