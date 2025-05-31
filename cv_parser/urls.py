from django.urls import path
from . import views

app_name = 'cv_parser'

urlpatterns = [
    path('upload/', views.upload_cv, name='upload_cv'),
    path('analyze/<int:user_id>/', views.analyze_cv, name='analyze_cv'),
]

