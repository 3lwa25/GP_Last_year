from django.contrib import admin
from .models import SimilarityResult

@admin.register(SimilarityResult)
class SimilarityResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'similarity_score', 'user', 'job', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('text1', 'text2', 'user__username', 'job__title')
    readonly_fields = ('similarity_score', 'tfidf_score', 'sbert_score')
