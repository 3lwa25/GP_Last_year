from django.db import models
from jobapp.models import Job, Applicant

class JobQuestion(models.Model):
    """Model to store questions generated for a specific job"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    is_general = models.BooleanField(default=False)
    skill_related = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Q for {self.job.title}: {self.question_text[:50]}..."

class ApplicantAnswer(models.Model):
    """Model to store applicant's answers to job questions"""
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(JobQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    audio_file = models.FileField(upload_to='applicant_answers/', null=True, blank=True)
    video_file = models.FileField(upload_to='applicant_videos/', null=True, blank=True)
    transcription = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Answer from {self.applicant.user.username} for {self.question.question_text[:30]}..."
