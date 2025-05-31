from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, FileResponse, Http404,JsonResponse
from django.shortcuts import render, redirect , get_object_or_404
from django.urls import reverse, reverse_lazy

from account.forms import *
from jobapp.permission import user_is_employee 
from account.models import User

def get_success_url(request):

    """
    Handle Success Url After LogIN

    """
    if 'next' in request.GET and request.GET['next'] != '':
        return request.GET['next']
    else:
        return reverse('jobapp:home')


def employee_registration(request):

    """
    Handle Employee Registration

    """
    form = EmployeeRegistrationForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.CV_file = request.FILES.get('CV_file')  
        user.save()
        return redirect('account:login')
    context={
        'form':form
    }
    return render(request,'account/employee-registration.html',context)



def employer_registration(request):

    """
    Handle Employee Registration 

    """

    form = EmployerRegistrationForm(request.POST or None)
    if form.is_valid():
        form = form.save()
        return redirect('account:login')
    context={
        'form':form
    }
    return render(request,'account/employer-registration.html',context)


@login_required(login_url=reverse_lazy('accounts:login'))
@user_is_employee
def employee_edit_profile(request, id=id):

    """
    Handle Employee Profile Update Functionality

    """

    user = get_object_or_404(User, id=id)
    form = EmployeeProfileEditForm(request.POST or None, request.FILES or None, instance=user)
    if form.is_valid():
        form = form.save()
        messages.success(request, 'Your Profile Was Successfully Updated!')
        return redirect(reverse("account:edit-profile", kwargs={
                                    'id': form.id
                                    }))
    context={
        'form':form
    }
    return render(request,'account/employee-edit-profile.html',context)

def user_logIn(request):

    """
    Provides users to logIn

    """

    form = UserLoginForm(request.POST or None)
    

    if request.user.is_authenticated:
        return redirect('/')
    
    else:
        if request.method == 'POST':
            if form.is_valid():
                auth.login(request, form.get_user())
                return HttpResponseRedirect(get_success_url(request))
    context = {
        'form': form,
    }
    return render(request,'account/login.html',context)


def user_logOut(request):
    """
    Provide the ability to logout
    """
    auth.logout(request)
    messages.success(request, 'You are Successfully logged out')
    return redirect('account:login')


@login_required
def view_cv(request, user_id):
    """
    Allows the employer to view the CV file of a job seeker.
    """

    if request.user.role != "employer":
        raise Http404("You are not allowed to view this file.")

    job_seeker = get_object_or_404(User, id=user_id)

    if not job_seeker.CV_file:
        raise Http404("No CV file available for this user.")

   
    return FileResponse(job_seeker.CV_file.open(), content_type='application/pdf')


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from account.models import User  # adjust if your User model is in another app
from datetime import datetime
from cv_parser.utils import parse_cv
from cv_parser.models import CVParser, CVAnalysis
import os

@login_required
def analyze_existing_cv(request, user_id):
    if request.user.role != "employer":
        raise Http404("Unauthorized access.")

    job_seeker = get_object_or_404(User, id=user_id)
    if not job_seeker.CV_file:
        raise Http404("CV file not found for this user.")

    file_path = job_seeker.CV_file.path
    parsed_data = parse_cv(file_path)

    if 'error' in parsed_data:
        return render(request, 'cv_parser/error.html', {'error': parsed_data['error']})

    # Save to CVAnalysis
    CVAnalysis.objects.update_or_create(
        user=job_seeker,
        defaults={
            'name': parsed_data.get('name'),
            'email': parsed_data.get('email'),
            'linkedin_link': parsed_data.get('linkedin'),
            'skills': ', '.join(parsed_data.get('skills', [])),
            'language': ', '.join(parsed_data.get('language', [])),
            'degree': ', '.join(parsed_data.get('degree', [])),
            'university': parsed_data.get('university', '')
        }
    )

    # Save to CVParser
    CVParser.objects.update_or_create(
        user=job_seeker,
        defaults={
            'cv_file_name': os.path.basename(file_path),
            'similarity_percent': parsed_data.get('similarity_percent'),
            'top_qualified_users': parsed_data.get('top_qualified_users'),
            'time_and_date': datetime.now()
        }
    )

    return render(request, 'cv_parser/results.html', {
        'parsed_data': parsed_data,
        'analyzed_user': job_seeker
    })

