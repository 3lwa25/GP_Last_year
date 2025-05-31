from django.urls import path
from account import views

app_name = "account"

urlpatterns = [
    path('employee/register/', views.employee_registration, name='employee-registration'),
    path('employer/register/', views.employer_registration, name='employer-registration'),
    path('profile/edit/<int:id>/', views.employee_edit_profile, name='edit-profile'),
    path('login/', views.user_logIn, name='login'),
    path('logout/', views.user_logOut, name='logout'),
    path('view-cv/<int:user_id>/', views.view_cv, name='view_cv'),
    path('analyze_cv/<int:user_id>/', views.analyze_existing_cv, name='analyze_cv'),
    path('edit-profile/<int:id>/', views.employee_edit_profile, name='edit-profile'),
]
