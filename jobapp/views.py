from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from .models import Video
from django.views.decorators.csrf import csrf_exempt
try:
    from whisper_vid_audio.utils import WhisperTranscriber
except ImportError:
    from whisper_vid_audio.transcribe import WhisperTranscriber
from cv_parser.models import CVAnalysis

from account.models import User
from jobapp.forms import *
from jobapp.models import *
from jobapp.permission import *
import os
import json

User = get_user_model()


def home_view(request):
    from django.utils import timezone
    
    # Update job status based on deadline before displaying
    today = timezone.now().date()
    all_published_jobs = Job.objects.filter(is_published=True)
    
    for job in all_published_jobs:
        if job.last_date < today:
            # Job deadline has passed - mark as closed
            if not job.is_closed:
                job.is_closed = True
                job.save()
        else:
            # Job deadline hasn't passed - mark as open
            if job.is_closed:
                job.is_closed = False
                job.save()

    published_jobs = Job.objects.filter(is_published=True).order_by('-timestamp')
    jobs = published_jobs.filter(is_closed=False)  # Only show open jobs on homepage
    total_candidates = User.objects.filter(role='employee').count()
    total_companies = User.objects.filter(role='employer').count()
    paginator = Paginator(jobs, 3)
    page_number = request.GET.get('page',None)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        job_lists=[]
        job_objects_list = page_obj.object_list.values()
        for job_list in job_objects_list:
            job_lists.append(job_list)
        

        next_page_number = None
        if page_obj.has_next():
            next_page_number = page_obj.next_page_number()

        prev_page_number = None       
        if page_obj.has_previous():
            prev_page_number = page_obj.previous_page_number()

        data={
            'job_lists':job_lists,
            'current_page_no':page_obj.number,
            'next_page_number':next_page_number,
            'no_of_page':paginator.num_pages,
            'prev_page_number':prev_page_number
        }    
        return JsonResponse(data)
    
    # Get REAL job titles and locations from ALL published jobs in database
    all_published_jobs = Job.objects.filter(is_published=True)
    job_titles = list(all_published_jobs.values_list('title', flat=True).distinct().order_by('title'))
    job_locations = list(all_published_jobs.values_list('location', flat=True).distinct().order_by('location'))
    
    # Clean the data - remove empty values
    job_titles = [title for title in job_titles if title and title.strip()]
    job_locations = [location for location in job_locations if location and location.strip()]
    
    # Debug output to help identify caching issues
    print(f"DEBUG: Sending {len(job_titles)} job titles to dropdown: {job_titles}")
    print(f"DEBUG: Sending {len(job_locations)} job locations to dropdown: {job_locations}")
    
    context = {
        'total_candidates': total_candidates,
        'total_companies': total_companies,
        'total_jobs': len(jobs),
        'total_completed_jobs':len(published_jobs.filter(is_closed=True)),
        'page_obj': page_obj,
        'job_titles': job_titles,
        'job_locations': job_locations
    }
    response = render(request, 'jobapp/index.html', context)
    # Add cache-busting headers to ensure fresh data
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


from django.shortcuts import render
from .models import Category  # Assuming the model name is Category
from jobapp.models import Category

def post_job(request):
    categories = Category.objects.all()  # Fetch all categories from the database
    form = JobForm(request.POST or None)  # Assuming your form is named JobForm
    
    if request.method == 'POST' and form.is_valid():
        # Handle form submission logic here
        form.save()
    
    return render(request, 'post-job.html', {
        'form': form,
        'categories': categories,  # Pass categories to the template
    })

def job_list_View(request):
    """
    Display all published jobs with deadline-based status control
    """
    from django.utils import timezone
    
    # Get all published jobs
    all_published_jobs = Job.objects.filter(is_published=True).order_by('-timestamp')
    
    # Update job status based on deadline
    today = timezone.now().date()
    for job in all_published_jobs:
        if job.last_date < today:
            # Job deadline has passed - mark as closed
            if not job.is_closed:
                job.is_closed = True
                job.save()
        else:
            # Job deadline hasn't passed - mark as open
            if job.is_closed:
                job.is_closed = False
                job.save()
    
    # Get fresh data after updating statuses
    job_list = Job.objects.filter(is_published=True).order_by('-timestamp')
    
    # Debug output to track job listing
    open_jobs = job_list.filter(is_closed=False).count()
    closed_jobs = job_list.filter(is_closed=True).count()
    print(f"DEBUG JOB LISTING: Found {job_list.count()} total published jobs ({open_jobs} open, {closed_jobs} closed)")
    
    paginator = Paginator(job_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_jobs': job_list.count(),
        'open_jobs': open_jobs,
        'closed_jobs': closed_jobs,
        'today': today,
    }
    
    # Add cache-busting headers to ensure fresh job data
    response = render(request, 'jobapp/job-list.html', context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# @login_required(login_url=reverse_lazy('account:login'))
# @user_is_employer
# def create_job_View(request):
#     """
#     Provide the ability to create job post
#     """
#     form = JobForm(request.POST or None)

#     user = get_object_or_404(User, id=request.user.id)
#     categories = Category.objects.all()

#     if request.method == 'POST':

#         if form.is_valid():

#             instance = form.save(commit=False)
#             instance.user = user
#             # Category can be optional (None)
#             instance.save()
#             # for save tags
#             form.save_m2m()
#             messages.success(
#                     request, 'You are successfully posted your job! Please wait for review.')
#             return redirect(reverse("jobapp:single-job", kwargs={
#                                     'id': instance.id
#                                     }))

@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def create_job_View(request):
    """
    Provide the ability to create job post
    """
    form = JobForm(request.POST or None)
    user = get_object_or_404(User, id=request.user.id)
    categories = Category.objects.all()

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = user
            instance.is_published = True  # Auto-publish jobs so they appear in search dropdowns
            instance.save()
            # for save tags
            form.save_m2m()
            messages.success(
                    request, 'You have successfully posted your job! It is now live and searchable.')
            return redirect(reverse("jobapp:single-job", kwargs={
                                    'id': instance.id
                                    }))

    context = {
        'form': form,
        'categories': categories
    }
    return render(request, 'jobapp/post-job.html', context)


@csrf_exempt
def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        new_video = Video(user=request.user, file=video_file)
        new_video.save()
        return JsonResponse({'status': 'success', 'message': 'Video uploaded successfully.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'No video file provided or wrong method.'})

def single_job_view(request, id):
    """
    Provide the ability to view job details
    """
    if cache.get(id):
        job = cache.get(id)
    else:
        job = get_object_or_404(Job, id=id)
        cache.set(id,job , 60 * 15)
    related_job_list = job.tags.similar_objects()

    paginator = Paginator(related_job_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'job': job,
        'page_obj': page_obj,
        'total': len(related_job_list)

    }
    return render(request, 'jobapp/job-single.html', context)


def search_result_view(request):
    """
        User can search job with multiple fields

    """

    job_list = Job.objects.filter(is_published=True).order_by('-timestamp')

    # Keywords
    if 'job_title_or_company_name' in request.GET:
        job_title_or_company_name = request.GET['job_title_or_company_name']

        if job_title_or_company_name:
            job_list = job_list.filter(title__icontains=job_title_or_company_name) | job_list.filter(
                company_name__icontains=job_title_or_company_name)

    # location
    if 'location' in request.GET:
        location = request.GET['location']
        if location:
            job_list = job_list.filter(location__icontains=location)

    # Job Type
    if 'job_type' in request.GET:
        job_type = request.GET['job_type']
        if job_type:
            job_list = job_list.filter(job_type__iexact=job_type)

    # Get all job titles and locations for the search dropdowns
    all_published_jobs = Job.objects.filter(is_published=True)
    job_titles = list(all_published_jobs.values_list('title', flat=True).distinct().order_by('title'))
    job_locations = list(all_published_jobs.values_list('location', flat=True).distinct().order_by('location'))
    
    # Clean the data - remove empty values
    job_titles = [title for title in job_titles if title and title.strip()]
    job_locations = [location for location in job_locations if location and location.strip()]

    # Debug output for search results page
    print(f"DEBUG SEARCH: Sending {len(job_titles)} job titles to search dropdown: {job_titles}")
    print(f"DEBUG SEARCH: Sending {len(job_locations)} job locations to search dropdown: {job_locations}")

    paginator = Paginator(job_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'job_titles': job_titles,
        'job_locations': job_locations,
        'total_results': job_list.count(),
    }
    response = render(request, 'jobapp/result.html', context)
    # Add cache-busting headers to search results too
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# Importing necessary modules
from similarity.utils import calculate_similarity_score
from whisper_vid_audio.transcribe import WhisperTranscriber
from .models import Applicant, Job
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def apply_job_view(request, id):
    """
       Handle job application process with video responses to interview questions.


    """
    user = get_object_or_404(User, id=request.user.id)
    job = get_object_or_404(Job, id=id)

    # Check if the user has already applied for this job
    if Applicant.objects.filter(user=user, job_id=id).exists():
        messages.error(request, 'You already applied for this job!')
        return redirect(reverse("jobapp:single-job", kwargs={'id': id}))

    if request.method == 'POST':
        form = JobApplyForm(request.POST, request.FILES)
        
        # Debug: Print form data and files
        print("POST data:", request.POST)
        print("FILES data:", request.FILES.keys())
        print("Form errors:", form.errors)

        if form.is_valid():
            # Check if at least the intro video file is provided
            if not request.FILES.get('video_intro'):
                messages.error(request, 'Video introduction is required!')
                return render(request, 'jobapp/apply_job.html', {'form': form, 'job': job})

              # Save the applicant details
            instance = form.save(commit=False)
            instance.user = user
            instance.job = job
            instance.save()

            try:
                # Process the intro video for similarity score
                intro_video = request.FILES.get('video_intro')
                
                # Save the video to the instance
                instance.video = intro_video
                instance.save()
                
                # Transcribe the intro video
                transcriber = WhisperTranscriber()
                result = transcriber.transcribe(instance.video.path)
                transcription = result.get('text', '')

                # Calculate similarity score between job description and transcription
                similarity_score = calculate_similarity_score(job.description, transcription)
                instance.transcription = transcription
                instance.similarity_score = similarity_score

                # Save transcription and similarity score
                instance.save()

                         # Import JobQuestion and ApplicantAnswer only if needed
                try:
                    from question_generation.models import JobQuestion, ApplicantAnswer
                    from question_generation.utils import generate_questions_for_job
                    
                    # Get or generate questions for this job
                    questions = JobQuestion.objects.filter(job=job)
                    if not questions.exists():
                        questions = generate_questions_for_job(job)
                    
                    # Process additional question videos if they exist
                    for key, file in request.FILES.items():
                        # Skip the intro video which we already processed
                        if key == 'video_intro':
                            continue
                            
                        if key.startswith('video_'):
                            # Extract the question ID from the field name (video_skill1, video_final, etc.)
                            question_id = key.replace('video_', '')
                            
                            # Find the corresponding question by ID
                            try:
                                # Try to extract numeric ID from question_id (e.g., skill1 -> 1, general3 -> 3)
                                if 'skill' in question_id:
                                    numeric_id = question_id.replace('skill', '')
                                elif 'general' in question_id:
                                    numeric_id = question_id.replace('general', '')
                                else:
                                    numeric_id = question_id
                                
                                # Get the question by its actual database ID
                                question = questions.filter(id=int(numeric_id)).first()
                                
                                if question:
                                    # Create answer record with video_file instead of audio_file
                                    answer = ApplicantAnswer(
                                        applicant=instance,
                                        question=question,
                                        video_file=file  # Use video_file field
                                    )
                                    answer.save()
                                    
                                    # Transcribe the video answer
                                    try:
                                        answer_result = transcriber.transcribe(answer.video_file.path)
                                        answer_transcription = answer_result.get('text', '').strip()
                                        
                                        # Save the transcription
                                        if answer_transcription:
                                            answer.answer_text = answer_transcription
                                            answer.transcription = answer_transcription
                                        else:
                                            answer.answer_text = "[No speech detected in the video]"
                                            answer.transcription = "[No speech detected in the video]"
                                        answer.save()
                                        print(f"Saved answer for question {question.id}: {answer_transcription[:100] if answer_transcription else 'No speech detected'}")
                                    except Exception as e:
                                        print(f"Error transcribing answer for question {question.id}: {str(e)}")
                                        answer.answer_text = f"[Transcription failed: {str(e)}]"
                                        answer.transcription = f"[Transcription failed: {str(e)}]"
                                        answer.save()
                                else:
                                    print(f"No question found for ID: {numeric_id}")
                            except (ValueError, TypeError) as e:
                                print(f"Error processing question ID {question_id}: {str(e)}")
                except ImportError:
                    # Question generation module not available
                    pass

                messages.success(request, 'You have successfully applied for this job!')
                return redirect(reverse("jobapp:single-job", kwargs={'id': id}))

            except Exception as e:
                # Clean up if something went wrong
                if instance.pk:
                    instance.delete()
                messages.error(request, f'Error during application process: {str(e)}')
                return render(request, 'jobapp/apply_job.html', {'form': form, 'job': job})
        else:
            # Form is not valid - provide detailed error information
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        error_messages.append(f"Form error: {error}")
                    else:
                        error_messages.append(f"{field}: {error}")
            
            # Check specifically for missing video_intro
            if not request.FILES.get('video_intro'):
                error_messages.append("Introduction video is required")
                
            print("Form validation errors:", error_messages)
            messages.error(request, f'Please correct the errors in the form: {", ".join(error_messages)}')
    else:
        form = JobApplyForm(initial={'job': job.id})

    # Try to get questions for this job
    questions = []
    try:
        from question_generation.models import JobQuestion
        from question_generation.utils import generate_questions_for_job
        
        # Get or generate questions for this job
        db_questions = JobQuestion.objects.filter(job=job)
        if not db_questions.exists():
            db_questions = generate_questions_for_job(job)
            
        # Convert to a format usable in the template
        for q in db_questions:
            question_type = 'general' if q.is_general else 'skill'
            # Use the actual question ID for proper mapping
            question_id = str(q.id)
            
            questions.append({
                'id': question_id,
                'text': q.question_text,
                'type': question_type,
                'skill': q.skill_related or '',
                'db_id': q.id  # Keep the database ID for reference
            })
    except ImportError:
        # Question generation module not available
        pass
        
    # Convert questions to JSON for the template
    questions_json = json.dumps(questions)
        
    return render(request, 'jobapp/apply_job.html', {
        'form': form, 
        'job': job,
        'questions_json': questions_json
    })


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import Applicant
from similarity.utils import calculate_similarity_score, analyze_text_similarity

@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def all_applicants_view(request, id):
    """
    View for employer to see all applicants and their similarity scores.
    """
    # Fetch all applicants for the given job id and order by similarity score (descending)
    all_applicants = Applicant.objects.filter(job=id)

    # Calculate similarity score for each applicant (if it's not already calculated)
    for applicant in all_applicants:
        if applicant.transcription:  # Ensure there's a transcription to compare with
            analysis = analyze_text_similarity(applicant.job.description, applicant.transcription)
            applicant.tfidf_score = analysis['tfidf_similarity']
            applicant.sbert_score = analysis['sbert_similarity']
            applicant.similarity_score = analysis['combined_score']
            applicant.save()

    # Order applicants by similarity score in descending order
    all_applicants = all_applicants.order_by('-similarity_score')

    context = {
        'all_applicants': all_applicants
    }

    return render(request, 'jobapp/all-applicants.html', context)


@login_required(login_url=reverse_lazy('account:login'))
def dashboard_view(request):
    """
    """
    jobs = []
    savedjobs = []
    appliedjobs = []
    total_applicants = {}
    if request.user.role == 'employer':

        jobs = Job.objects.filter(user=request.user.id)
        for job in jobs:
            count = Applicant.objects.filter(job=job.id).count()
            total_applicants[job.id] = count

    if request.user.role == 'employee':
        savedjobs = BookmarkJob.objects.filter(user=request.user.id)
        appliedjobs = Applicant.objects.filter(user=request.user.id)
    context = {

        'jobs': jobs,
        'savedjobs': savedjobs,
        'appliedjobs':appliedjobs,
        'total_applicants': total_applicants
    }

    return render(request, 'jobapp/dashboard.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def delete_job_view(request, id):

    job = get_object_or_404(Job, id=id, user=request.user.id)

    if job:

        job.delete()
        messages.success(request, 'Your Job Post was successfully deleted!')

    return redirect('jobapp:dashboard')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def make_complete_job_view(request, id):
    job = get_object_or_404(Job, id=id, user=request.user.id)

    if job:
        try:
            job.is_closed = True
            job.save()
            messages.success(request, 'Your Job was marked closed!')
        except:
            messages.success(request, 'Something went wrong !')
            
    return redirect('jobapp:dashboard')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def delete_bookmark_view(request, id):

    job = get_object_or_404(BookmarkJob, id=id, user=request.user.id)

    if job:

        job.delete()
        messages.success(request, 'Saved Job was successfully deleted!')

    return redirect('jobapp:dashboard')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def applicant_details_view(request, id):
    applicant = get_object_or_404(User, id=id)
    
    # Get application video and details
    job_id = request.GET.get('job_id')
    
    # If job_id is provided, get the specific application
    if job_id:
        application = Applicant.objects.filter(
            user=applicant,
            job_id=job_id
        ).first()
    else:
        # Otherwise get the most recent application
        application = Applicant.objects.filter(
            user=applicant
        ).order_by('-timestamp').first()
        
    # Get all jobs this applicant has applied to
    applied_jobs = Applicant.objects.filter(user=applicant)
    
    # Get CV analysis data if available
    try:
        cv_analysis = CVAnalysis.objects.get(user=applicant)
    except CVAnalysis.DoesNotExist:
        cv_analysis = None
    
    context = {
        'applicant': applicant,
        'application': application,
        'applied_jobs': applied_jobs,
        'cv_analysis': cv_analysis,
    }

    return render(request, 'jobapp/applicant-details.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def job_bookmark_view(request, id):

    form = JobBookmarkForm(request.POST or None)

    user = get_object_or_404(User, id=request.user.id)
    applicant = BookmarkJob.objects.filter(user=request.user.id, job=id)

    if not applicant:
        if request.method == 'POST':

            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = user
                instance.save()

                messages.success(
                    request, 'You have successfully save this job!')
                return redirect(reverse("jobapp:single-job", kwargs={
                    'id': id
                }))

        else:
            return redirect(reverse("jobapp:single-job", kwargs={
                'id': id
            }))

    else:
        messages.error(request, 'You already saved this Job!')

        return redirect(reverse("jobapp:single-job", kwargs={
            'id': id
        }))


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def job_edit_view(request, id=id):
    """
    Handle Job Update
    """
    job = get_object_or_404(Job, id=id, user=request.user.id)
    form = JobEditForm(request.POST or None, instance=job)
    categories = Category.objects.all()
    
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        # for save tags
        # form.save_m2m()
        messages.success(request, 'Your Job Post Was Successfully Updated!')
        return redirect(reverse("jobapp:single-job", kwargs={
            'id': instance.id
        }))
    
    context = {
        'form': form,
        'categories': categories
    }
    return render(request, 'jobapp/job-edit.html', context)

def about_us(request):
    return render(request, "jobapp/about_us.html", {})

def contact(request):
    """
    Simple contact form handler with console output
    """
    import logging
    from datetime import datetime
    
    # Configure logging for this view
    logger = logging.getLogger(__name__)
    
    form = ContactForm(request.POST or None)
    
    if request.method == "POST":
        email = request.POST.get('email')
        name = request.POST.get('name')
        message = request.POST.get('message')
        
        # Validate form data
        if not all([email, name, message]):
            messages.error(request, 'Please fill in all required fields.')
            logger.warning(f"Incomplete contact form submission from {request.META.get('REMOTE_ADDR', 'unknown')}")
        else:
            # Log the contact attempt
            logger.info(f"📧 Contact form submission from {name} ({email})")
            
            # Display message in console
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            print(f"\n{'='*80}")
            print(f"📧 NEW CONTACT FORM SUBMISSION")
            print(f"{'='*80}")
            print(f"📅 Submitted: {current_time}")
            print(f"👤 Name: {name}")
            print(f"📧 Email: {email}")
            print(f"🌍 IP Address: {request.META.get('REMOTE_ADDR', 'Unknown')}")
            print(f"{'='*80}")
            print(f"💬 MESSAGE:")
            print(f"{'-'*40}")
            print(f"{message}")
            print(f"{'='*80}")
            print(f"📍 Contact them at: {email}")
            print(f"{'='*80}\n")
            
            # Show success message to user
            messages.success(request, 
                '✅ Thank you for your message! We have received your inquiry and will get back to you soon.')
            logger.info(f"✅ Contact form processed successfully for {name}")
            
            # Redirect to clear the form
            return redirect(request.path + '?sent=1')
    
    # Handle success redirect parameter
    if request.GET.get('sent') == '1':
        messages.success(request, '✅ Your message has been received! We will contact you soon.')
    
    context = {
        'form': form,
    }
    
    return render(request, "jobapp/contact.html", context)