from django.urls import path
from . import views

app_name = 'similarity'

urlpatterns = [
    path('detailed-analysis/', views.detailed_similarity_analysis_view, name='detailed-analysis'),
    path('applicant-analysis/', views.detailed_applicant_analysis_view, name='detailed-analysis'),
]
