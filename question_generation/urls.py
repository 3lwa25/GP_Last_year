from django.urls import path
from . import views

app_name = 'question_generation'

urlpatterns = [
    path('generate_questions/<int:job_id>/', views.generate_job_questions, name='generate_job_questions'),
    path('view_questions/<int:job_id>/', views.view_job_questions, name='view_job_questions'),
    path('answer_questions/<int:job_id>/', views.answer_job_questions, name='answer_job_questions'),
    path('applicant/<int:applicant_id>/job/<int:job_id>/answers/', views.view_applicant_answers, name='view_applicant_answers'),
    path('applicant/<int:applicant_id>/job/<int:job_id>/answers/preview/', views.video_answers_preview, name='video_answers_preview'),
    path('test/', views.test_question_generation, name='test_question_generation'),
    path('debug-transcriptions/', views.debug_transcriptions, name='debug_transcriptions'),
] 