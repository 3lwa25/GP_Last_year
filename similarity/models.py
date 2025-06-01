from django.db import models
from django.contrib.auth import get_user_model
from jobapp.models import Job

User = get_user_model()

class SimilarityResult(models.Model):
    """
    Model to store similarity analysis results independently of job applications
    This allows for standalone similarity comparisons
    """
    text1 = models.TextField()
    text2 = models.TextField()
    similarity_score = models.FloatField()
    tfidf_score = models.FloatField()
    sbert_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Similarity Result"
        verbose_name_plural = "Similarity Results"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Similarity: {self.similarity_score:.2f} ({self.created_at.strftime('%Y-%m-%d')})"
