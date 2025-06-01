import os
import re
import json
import time
import random
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv
from django.conf import settings

# Load environment variables
load_dotenv()

# Get API key from environment variable or settings
api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
if not api_key:
    raise ValueError("Please set the GEMINI_API_KEY in .env file or settings.py")

# Verify API key isn't the placeholder
if api_key == "YOUR_GEMINI_API_KEY":
    print("WARNING: Using placeholder Gemini API key. Replace with actual key in settings.py or .env file")

# Configure Gemini
try:
    genai.configure(api_key=api_key)
    print(f"Gemini API configured with key: {api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:] if len(api_key) > 8 else ''}")
except Exception as e:
    print(f"Error configuring Gemini API: {str(e)}")

def test_gemini_api():
    """Test if the Gemini API is working properly"""
    try:
        result = gemini_prompt("Hello, please respond with 'The API is working correctly.' if you receive this message.")
        print(f"Gemini API test result: {result}")
        return result == "The API is working correctly."
    except Exception as e:
        print(f"Gemini API test failed: {str(e)}")
        return False

def gemini_prompt(prompt: str, temperature=0.7, max_retries=5) -> str:
    """Send a prompt to the Gemini API and get a response"""
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Initialize the model with safety settings
            generation_config = {
                "temperature": temperature,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }
            
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
            ]
            
            model = genai.GenerativeModel(model_name="models/gemini-1.5-flash",
                                        generation_config=generation_config,
                                        safety_settings=safety_settings)
            
            response = model.generate_content(prompt)
            
            if response.text is None:
                raise ValueError("Empty response from Gemini API")
                
            return response.text.strip()
        except Exception as e:
            error_message = str(e)
            print(f"Error in gemini_prompt (attempt {retry_count+1}/{max_retries}): {error_message}")
            
            # If it's a rate limit error, retry with exponential backoff
            if "429" in error_message and retry_count < max_retries - 1:
                # Exponential backoff with jitter
                sleep_time = (2 ** retry_count) + random.random()
                print(f"Rate limited. Retrying in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
                retry_count += 1
            else:
                # For other errors or if we've reached max retries, raise the exception
                raise

def extract_skills_from_job_description(job_description: str) -> List[str]:
    """Extract skills from a job description"""
    # Truncate job description if too long to avoid token limits
    max_chars = 4000
    truncated_description = job_description[:max_chars] + ("..." if len(job_description) > max_chars else "")
    
    prompt = f"""
    Extract a list of key technical skills and qualifications from the job description below.
    Provide only a plain list of skills, one per line, no extra comments.

    Job Description:
    {truncated_description}
    """
    skills_text = gemini_prompt(prompt, temperature=0.3)
    return [re.sub(r'^[\d\-\•\*]+\.?\s*', '', s.strip()) for s in skills_text.splitlines() if s.strip()]

def extract_skills_from_resume(resume_text: str) -> List[str]:
    """Extract skills from a resume"""
    # Truncate resume if too long to avoid token limits
    max_chars = 4000
    truncated_resume = resume_text[:max_chars] + ("..." if len(resume_text) > max_chars else "")
    
    prompt = f"""
    Extract a list of key technical skills and qualifications from the resume below.
    Provide only a plain list of skills, one per line, no extra comments.

    Resume:
    {truncated_resume}
    """
    skills_text = gemini_prompt(prompt, temperature=0.3)
    return [re.sub(r'^[\d\-\•\*]+\.?\s*', '', s.strip()) for s in skills_text.splitlines() if s.strip()]

def generate_questions_for_skill(skill: str, job_title: str) -> List[str]:
    """Generate questions to assess a specific skill"""
    prompt = f"""
    Generate 2 interview questions to evaluate a candidate's expertise in {skill} for a {job_title} role.
    Include:
    - A practical/technical question
    - A behavioral question if suitable

    Return only the questions, one per line.
    """
    questions_text = gemini_prompt(prompt)
    return [re.sub(r'^[\d\-\•\*]+\.?\s*', '', q.strip()) for q in questions_text.splitlines() if q.strip()]

def generate_general_questions(job_title: str, job_description: str) -> List[str]:
    """Generate general interview questions for a job"""
    # Truncate job description if too long
    max_chars = 500
    truncated_description = job_description[:max_chars] + ("..." if len(job_description) > max_chars else "")
    
    prompt = f"""
    Write 4 general interview questions for a {job_title} role focused on:
    - Culture fit
    - Problem-solving
    - Teamwork
    - Career goals
    Base your questions on this job description:

    {truncated_description}

    Return just the questions, one per line.
    """
    questions_text = gemini_prompt(prompt)
    return [re.sub(r'^[\d\-\•\*]+\.?\s*', '', q.strip()) for q in questions_text.splitlines() if q.strip()]

def generate_interview_questions(job_title: str, job_description: str, cv_skills=None, max_skill_questions: int = 3) -> Dict[str, Any]:
    """Generate tailored interview questions based on job description and CV skills"""
    # Extract skills from job description
    job_skills = extract_skills_from_job_description(job_description)
    
    # If CV skills are provided, find common skills to focus questions on
    if cv_skills and isinstance(cv_skills, list) and len(cv_skills) > 0:
        # Find common skills between job and CV (case insensitive)
        job_skills_lower = [s.lower() for s in job_skills]
        cv_skills_lower = [s.lower() for s in cv_skills]
        common_skills = list(set(job_skills_lower).intersection(set(cv_skills_lower)))
        
        # If we found common skills, prioritize them
        if common_skills:
            # Map back to original case for better readability
            prioritized_skills = []
            for skill_lower in common_skills:
                for skill in job_skills:
                    if skill.lower() == skill_lower and skill not in prioritized_skills:
                        prioritized_skills.append(skill)
                        break
            
            # Add other job skills until we reach the limit
            for skill in job_skills:
                if skill.lower() not in common_skills and len(prioritized_skills) < max_skill_questions:
                    prioritized_skills.append(skill)
            
            skills_to_use = prioritized_skills[:max_skill_questions]
        else:
            skills_to_use = job_skills[:max_skill_questions]
    else:
        skills_to_use = job_skills[:max_skill_questions]
    
    # Generate skill-specific questions
    skill_questions = {}
    for skill in skills_to_use:
        questions = generate_questions_for_skill(skill, job_title)
        skill_questions[skill] = questions
        # Add a small delay to avoid hitting rate limits
        time.sleep(1)

    # Generate general questions
    general_questions = generate_general_questions(job_title, job_description)

    return {
        "job_title": job_title,
        "skills_identified": job_skills,
        "skill_questions": skill_questions,
        "general_questions": general_questions,
        "total_questions": sum(len(qs) for qs in skill_questions.values()) + len(general_questions)
    }

def generate_questions_for_job(job, cv_skills=None):
    """Generate questions for a job and save them to the database"""
    from question_generation.models import JobQuestion
    
    # Log that we're starting question generation
    print(f"Starting question generation for job: {job.title} (ID: {job.id})")
    
    try:
        # Delete existing questions for this job
        JobQuestion.objects.filter(job=job).delete()
        
        # Generate new questions
        questions_data = generate_interview_questions(
            job_title=job.title, 
            job_description=job.description,
            cv_skills=cv_skills
        )
        
        print(f"Generated questions data with {len(questions_data['general_questions'])} general questions and {len(questions_data['skill_questions'])} skill categories")
        
        # Count questions we'll create
        total_questions = len(questions_data["general_questions"])
        for skill, questions in questions_data["skill_questions"].items():
            total_questions += len(questions)
        
        print(f"Creating {total_questions} questions in the database")
        
        question_objects = []
        
        # Save skill-specific questions
        for skill, questions in questions_data["skill_questions"].items():
            for q_text in questions:
                question = JobQuestion.objects.create(
                    job=job,
                    question_text=q_text,
                    is_general=False,
                    skill_related=skill
                )
                question_objects.append(question)
        
        # Save general questions
        for q_text in questions_data["general_questions"]:
            question = JobQuestion.objects.create(
                job=job,
                question_text=q_text,
                is_general=True
            )
            question_objects.append(question)
        
        print(f"Successfully created {len(question_objects)} questions")
        return JobQuestion.objects.filter(job=job)
    
    except Exception as e:
        print(f"Error in generate_questions_for_job: {str(e)}")
        # Try to create a few default questions if there was an error
        try:
            default_questions = [
                "Tell me about yourself and why you're interested in this position.",
                "What are your strongest skills relevant to this role?",
                "Describe a challenging project you worked on and how you overcame obstacles.",
                "How do you handle tight deadlines and pressure?",
                "Do you have any questions about the role or company?"
            ]
            
            for i, q_text in enumerate(default_questions):
                JobQuestion.objects.create(
                    job=job,
                    question_text=q_text,
                    is_general=True
                )
            
            print(f"Created {len(default_questions)} default questions due to error")
            return JobQuestion.objects.filter(job=job)
        except Exception as inner_e:
            print(f"Error creating default questions: {str(inner_e)}")
            return JobQuestion.objects.none()
