from django.contrib import admin
from .models import JobQuestion, ApplicantAnswer

@admin.register(JobQuestion)
class JobQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'question_text_short', 'is_general', 'skill_related', 'created_at')
    list_filter = ('is_general', 'created_at')
    search_fields = ('question_text', 'skill_related')
    ordering = ('-created_at',)
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    
    question_text_short.short_description = 'Question'

@admin.register(ApplicantAnswer)
class ApplicantAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'question_short', 'answer_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('answer_text', 'transcription')
    ordering = ('-created_at',)
    
    def question_short(self, obj):
        return obj.question.question_text[:50] + '...' if len(obj.question.question_text) > 50 else obj.question.question_text
    
    def answer_short(self, obj):
        return obj.answer_text[:50] + '...' if len(obj.answer_text) > 50 else obj.answer_text
    
    question_short.short_description = 'Question'
    answer_short.short_description = 'Answer'
