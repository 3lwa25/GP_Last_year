from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from jobapp.models import Applicant, Job  # Import Applicant from jobapp
from jobapp.permission import user_is_employer
from .utils import analyze_text_similarity, extract_keywords
from .models import SimilarityResult

@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def detailed_similarity_analysis_view(request):
    """Detailed similarity analysis view"""
    # Implementation for detailed similarity analysis
    return render(request, 'similarity/detailed_analysis.html', {})

@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def detailed_applicant_analysis_view(request):
    """Detailed analysis for a specific applicant's similarity score"""
    applicant_id = request.GET.get('applicant_id')
    if not applicant_id:
        return redirect('jobapp:dashboard')
    
    # Get applicant data
    applicant = get_object_or_404(Applicant, id=applicant_id)
    
    # Ensure the employer owns the job
    if request.user.id != applicant.job.user.id and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this analysis')
        return redirect('jobapp:dashboard')
    
    # Get detailed analysis
    if not applicant.transcription or not applicant.job.description:
        messages.error(request, 'Missing data needed for analysis')
        return redirect('jobapp:dashboard')
        
    analysis = analyze_text_similarity(
        applicant.job.description, 
        applicant.transcription,
        verbose=True
    )
    
    # Extract keywords for visualization
    job_keywords = extract_keywords(applicant.job.description, 15)
    transcription_keywords = extract_keywords(applicant.transcription, 15)
    common_keywords = list(set(job_keywords) & set(transcription_keywords))
    
    # Calculate percentages for template
    percentages = {
        'similarity_score': int(applicant.similarity_score * 100),
        'tfidf_similarity': int(analysis['tfidf_similarity'] * 100),
        'sbert_similarity': int(analysis['sbert_similarity'] * 100),
        'keyword_overlap': int(analysis['keyword_overlap'] * 100),
        'chunk_similarity': int(analysis['chunk_similarity'] * 100)
    }
    
    context = {
        'applicant': applicant,
        'analysis': analysis,
        'percentages': percentages,
        'job_keywords': job_keywords,
        'transcription_keywords': transcription_keywords,
        'common_keywords': common_keywords,
    }
    
    return render(request, 'similarity/applicant_analysis.html', context)
