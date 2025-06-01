from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages

from .models import JobQuestion, ApplicantAnswer
from jobapp.models import Job, Applicant
from jobapp.permission import user_is_employer, user_is_employee
from .utils import generate_questions_for_job, test_gemini_api
from whisper_vid_audio.transcribe import WhisperTranscriber

def test_question_generation(request):
    """Test the question generation functionality"""
    if not request.user.is_superuser:
        return HttpResponse("Access denied. Only superusers can run this test.")
    
    api_working = test_gemini_api()
    
    response_data = {
        "api_test": "Success" if api_working else "Failed",
    }
    
    # If the API is working, try generating questions for a job
    if api_working:
        try:
            # Get a job to test with
            job = Job.objects.filter(is_published=True).first()
            
            if job:
                # Clear existing questions
                JobQuestion.objects.filter(job=job).delete()
                
                # Generate new questions
                questions = generate_questions_for_job(job)
                
                # Add results to response
                response_data["job_title"] = job.title
                response_data["questions_generated"] = questions.count()
                response_data["sample_questions"] = [q.question_text for q in questions[:3]]
            else:
                response_data["job_test"] = "No published jobs found to test with"
        except Exception as e:
            response_data["job_test_error"] = str(e)
    
    return JsonResponse(response_data)

@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def generate_job_questions(request, job_id):
    """Generate questions for a specific job"""
    job = get_object_or_404(Job, id=job_id, user=request.user)
    
    # Generate questions
    questions = generate_questions_for_job(job)
    
    messages.success(request, f'Successfully generated {questions.count()} questions for "{job.title}"')
    return redirect('jobapp:single-job', id=job_id)

@login_required(login_url=reverse_lazy('account:login'))
def view_job_questions(request, job_id):
    """View questions for a specific job"""
    job = get_object_or_404(Job, id=job_id)
    
    # If no questions exist, generate them for employers
    questions = JobQuestion.objects.filter(job=job)
    if not questions.exists() and request.user.id == job.user.id:
        questions = generate_questions_for_job(job)
    
    # Get general and skill-specific questions
    general_questions = questions.filter(is_general=True)
    skill_questions = questions.filter(is_general=False)
    
    # Group skill questions by skill
    skills_dict = {}
    for question in skill_questions:
        skill = question.skill_related or "Other"
        if skill not in skills_dict:
            skills_dict[skill] = []
        skills_dict[skill].append(question)
    
    context = {
        'job': job,
        'general_questions': general_questions,
        'skills_dict': skills_dict,
        'total_questions': questions.count()
    }
    
    return render(request, 'question_generation/view_questions.html', context)

@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def answer_job_questions(request, job_id):
    """Answer questions for a job application"""
    job = get_object_or_404(Job, id=job_id)
    
    # Check if the user has applied for this job
    try:
        applicant = Applicant.objects.get(user=request.user, job=job)
    except Applicant.DoesNotExist:
        messages.error(request, 'You must apply for this job before answering questions.')
        return redirect('jobapp:single-job', id=job_id)
    
    # Get questions for this job
    questions = JobQuestion.objects.filter(job=job)
    
    # If no questions exist, generate them
    if not questions.exists():
        questions = generate_questions_for_job(job)
    
    # Check if all questions have been answered
    answered_questions = ApplicantAnswer.objects.filter(applicant=applicant).values_list('question__id', flat=True)
    unanswered_questions = questions.exclude(id__in=answered_questions)
    
    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        video_file = request.FILES.get('video_file')
        
        if not question_id or not video_file:
            messages.error(request, 'Question ID and video file are required.')
            return redirect('question_generation:answer_job_questions', job_id=job_id)
        
        # Get the question
        question = get_object_or_404(JobQuestion, id=question_id, job=job)
        
        # Create a new answer
        answer = ApplicantAnswer(
            applicant=applicant,
            question=question,
            video_file=video_file
        )
        answer.save()
        
        # Transcribe the video file
        transcription_successful = False
        try:
            from whisper_vid_audio.transcribe import WhisperTranscriber
            transcriber = WhisperTranscriber()
            
            # Check if the video file exists and is accessible
            if not answer.video_file or not answer.video_file.path:
                raise Exception("Video file path is not available")
            
            print(f"Starting transcription for video: {answer.video_file.path}")
            result = transcriber.transcribe(answer.video_file.path)
            transcription = result.get('text', '').strip()
            
            if transcription:
                # Save the transcription to both fields for compatibility
                answer.answer_text = transcription
                answer.transcription = transcription
                answer.save()
                transcription_successful = True
                print(f"Transcription successful: {transcription[:100]}...")
                messages.success(request, f'Your video answer has been recorded and transcribed successfully! ({len(transcription)} characters transcribed)')
            else:
                answer.answer_text = "[No speech detected in the video]"
                answer.transcription = "[No speech detected in the video]"
                answer.save()
                messages.warning(request, 'Your video answer has been recorded, but no speech was detected during transcription.')
            
        except ImportError as e:
            print(f"Whisper module import error: {e}")
            answer.answer_text = "[Transcription service not available]"
            answer.transcription = "[Transcription service not available]"
            answer.save()
            messages.warning(request, 'Your video answer has been recorded, but transcription service is currently unavailable.')
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            answer.answer_text = f"[Transcription failed: {str(e)}]"
            answer.transcription = f"[Transcription failed: {str(e)}]"
            answer.save()
            messages.warning(request, f'Your video answer has been recorded, but transcription failed: {str(e)}')
        
        # Redirect to the same page to continue answering questions
        return redirect('question_generation:answer_job_questions', job_id=job_id)
    
    context = {
        'job': job,
        'applicant': applicant,
        'questions': questions,
        'unanswered_questions': unanswered_questions,
        'answered_count': len(answered_questions),
        'total_count': questions.count()
    }
    
    return render(request, 'question_generation/answer_questions.html', context)

@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def view_applicant_answers(request, applicant_id, job_id):
    """View an applicant's answers to job questions"""
    job = get_object_or_404(Job, id=job_id, user=request.user)
    applicant = get_object_or_404(Applicant, id=applicant_id, job=job)
    
    # Get questions and answers from question_generation app
    questions = JobQuestion.objects.filter(job=job)
    formal_answers = ApplicantAnswer.objects.filter(applicant=applicant)
    
    # Debug information
    print(f"Debug - Job ID: {job_id}, Applicant ID: {applicant_id}")
    print(f"Debug - Questions for this job: {questions.count()}")
    print(f"Debug - Formal answers for this applicant: {formal_answers.count()}")
    
    # Try to get video responses from job application process (if model exists)
    video_responses = []
    try:
        from jobapp.models import QuestionResponse
        video_responses = QuestionResponse.objects.filter(applicant=applicant)
        print(f"Debug - Video responses: {len(video_responses)}")
    except ImportError:
        # QuestionResponse model doesn't exist, skip video responses
        print("Debug - QuestionResponse model not available")
        pass
    
    # Create a dictionary of formal answers keyed by question
    formal_answers_dict = {answer.question.id: answer for answer in formal_answers}
    
    # Prepare data for template
    questions_with_answers = []
    
    # Add ALL formal questions (whether they have answers or not)
    for question in questions:
        answer = formal_answers_dict.get(question.id)
        questions_with_answers.append({
            'question': question,
            'answer': answer,  # This will be None if no answer exists
            'type': 'formal'
        })
        print(f"Debug - Question {question.id}: {'Has answer' if answer else 'No answer'}")
    
    # Add video responses as pseudo-questions (if any exist)
    for video_response in video_responses:
        # Create a pseudo-question object for video responses
        pseudo_question = type('obj', (object,), {
            'question_text': video_response.question_text,
            'is_general': True,  # Default to general
            'skill_related': video_response.question_id,  # Use question_id as skill
            'id': f"video_{video_response.question_id}"
        })
        
        # Create a pseudo-answer object that matches the template expectations
        pseudo_answer = type('obj', (object,), {
            'answer_text': video_response.transcription,
            'audio_file': video_response.video,  # Video file as audio file for template
            'created_at': video_response.created_at
        })
        
        questions_with_answers.append({
            'question': pseudo_question,
            'answer': pseudo_answer,
            'type': 'video'
        })
    
    # Calculate total counts
    total_formal_answers = formal_answers.count()
    total_video_responses = len(video_responses)
    total_answers = total_formal_answers + total_video_responses
    total_questions = questions.count()
    
    print(f"Debug - Total questions: {total_questions}, Total answers: {total_answers}")
    
    context = {
        'job': job,
        'applicant': applicant,
        'questions_with_answers': questions_with_answers,
        'answered_count': total_answers,
        'total_count': max(total_questions, total_video_responses),  # Show the higher count
        'formal_answers_count': total_formal_answers,
        'video_responses_count': total_video_responses,
    }
    
    return render(request, 'question_generation/view_answers.html', context)

@login_required
def debug_transcriptions(request):
    """Debug view to check transcription status - only for superusers"""
    if not request.user.is_superuser:
        return HttpResponse("Access denied. Only superusers can access this debug view.")
    
    answers = ApplicantAnswer.objects.all().order_by('-created_at')
    
    debug_info = []
    for answer in answers:
        debug_info.append({
            'id': answer.id,
            'applicant': answer.applicant.user.username,
            'question': answer.question.question_text[:50] + "...",
            'video_file': bool(answer.video_file),
            'video_path': answer.video_file.name if answer.video_file else None,
            'has_answer_text': bool(answer.answer_text),
            'answer_text_length': len(answer.answer_text) if answer.answer_text else 0,
            'has_transcription': bool(answer.transcription),
            'transcription_length': len(answer.transcription) if answer.transcription else 0,
            'created_at': answer.created_at,
            'answer_text_preview': answer.answer_text[:100] + "..." if answer.answer_text and len(answer.answer_text) > 100 else answer.answer_text
        })
    
    context = {
        'debug_info': debug_info,
        'total_answers': len(debug_info)
    }
    
    return JsonResponse(context, safe=False)

@login_required
@user_is_employer
def video_answers_preview(request, applicant_id, job_id):
    """AJAX endpoint to get a preview of video answers for modal display"""
    job = get_object_or_404(Job, id=job_id, user=request.user)
    applicant = get_object_or_404(Applicant, id=applicant_id, job=job)
    
    # Get answers from question_generation app
    answers = ApplicantAnswer.objects.filter(applicant=applicant).select_related('question')
    
    preview_data = []
    for answer in answers:
        answer_data = {
            'question_text': answer.question.question_text,
            'transcription': answer.answer_text or answer.transcription,
            'video_url': answer.video_file.url if answer.video_file else None,
            'created_at': answer.created_at.strftime('%Y-%m-%d %H:%M:%S') if answer.created_at else None
        }
        preview_data.append(answer_data)
    
    response_data = {
        'success': True,
        'answers': preview_data,
        'total_count': len(preview_data),
        'applicant_info': {
            'name': applicant.user.get_full_name(),
            'email': applicant.user.email,
            'user_id': applicant.user.id,
            'applied_date': applicant.timestamp.strftime('%B %d, %Y') if applicant.timestamp else None,
            'similarity_score': round(applicant.similarity_score, 1) if applicant.similarity_score else 0,
        },
        'job_title': job.title
    }
    
    if not preview_data:
        response_data.update({
            'success': False,
            'message': 'This applicant has not answered any video questions yet.'
        })
    
    return JsonResponse(response_data)
