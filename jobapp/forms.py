# from django import forms
# from django.contrib.auth import authenticate
# from django.contrib.auth import get_user_model
# from django.contrib import auth
# from jobapp.models import *
# from ckeditor.widgets import CKEditorWidget

# User = get_user_model()


# class ContactForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(ContactForm, self).__init__(*args, **kwargs)
#         self.fields['Email'].widget.attrs['placeholder'] = 'Enter a valid E-mail'

#     class Meta:
#         model = Contact
#         fields = [
#             'Email',
#             'name',
#             'message',
#         ]


# class JobForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(JobForm, self).__init__(*args, **kwargs)
#         # Customize labels
#         self.fields['title'].label = "Job Title :"
#         self.fields['location'].label = "Job Location :"
#         self.fields['salary'].label = "Salary :"
#         self.fields['Vacancy'].label = "Vacancy :"
#         self.fields['passedout'].label = "Year of Passed out :"
#         self.fields['description'].label = "Job Description :"
#         self.fields['Experience'].label = "Experience :"
#         self.fields['tags'].label = "Tags :"
#         self.fields['gender'].label = "Gender :"
#         self.fields['last_date'].label = "Submission Deadline :"
#         self.fields['company_name'].label = "Company Name :"
#         self.fields['url'].label = "Website :"
#         self.fields['category'].label = "Category :"
#         self.fields['job_type'].label = "Job Type :"

#         # Customize widgets (placeholders)
#         self.fields['title'].widget.attrs.update({'placeholder': 'eg : Software Developer'})
#         self.fields['location'].widget.attrs.update({'placeholder': 'eg : Karaikal, Puducherry'})
#         self.fields['salary'].widget.attrs.update({'placeholder': '********'})
#         self.fields['Vacancy'].widget.attrs.update({'placeholder': ''})
#         self.fields['passedout'].widget.attrs.update({'placeholder': ''})
#         self.fields['Experience'].widget.attrs.update({'placeholder': ''})
#         self.fields['tags'].widget.attrs.update({'placeholder': 'eg: Python, JavaScript'})
#         self.fields['gender'].widget.attrs.update({'placeholder': ''})
#         self.fields['last_date'].widget.attrs.update({'placeholder': 'YYYY-MM-DD'})
#         self.fields['company_name'].widget.attrs.update({'placeholder': 'Company Name'})
#         self.fields['url'].widget.attrs.update({'placeholder': 'https://example.com'})
#         # Ensure category and job_type are displayed as dropdowns
#         self.fields['category'].widget = forms.Select()
#         self.fields['job_type'].widget = forms.Select()

#     class Meta:
#         model = Job
#         fields = [
#             "title",
#             "location",
#             "job_type",
#             "category",
#             "Vacancy",
#             "passedout",
#             "salary",
#             "description",
#             "Experience",
#             "tags",
#             "gender",
#             "last_date",
#             "company_name",
#             "company_description",
#             "url"
#         ]

#     def clean_job_type(self):
#         job_type = self.cleaned_data.get('job_type')
#         if not job_type:
#             raise forms.ValidationError("Job Type is required")
#         return job_type

#     def clean_category(self):
#         category = self.cleaned_data.get('category')
#         if not category:
#             raise forms.ValidationError("Category is required")
#         return category

#     def save(self, commit=True):
#         job = super(JobForm, self).save(commit=False)
#         if commit:
#             job.save()
#             self.save_m2m()  # Save tags (ManyToMany relationship)
#         return job


from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib import auth
from jobapp.models import *
from ckeditor.widgets import CKEditorWidget

User = get_user_model()


class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['Email'].widget.attrs['placeholder'] = 'Enter a valid E-mail'

    class Meta:
        model = Contact
        fields = [
            'Email',
            'name',
            'message',
        ]


class JobForm(forms.ModelForm):
    # Explicitly define the category field as ModelChoiceField
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a Category",
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        # Customize labels
        self.fields['title'].label = "Job Title :"
        self.fields['location'].label = "Job Location :"
        self.fields['salary'].label = "Salary :"
        self.fields['Vacancy'].label = "Vacancy :"
        self.fields['passedout'].label = "Year of Passed out :"
        self.fields['description'].label = "Job Description :"
        self.fields['Experience'].label = "Experience :"
        self.fields['tags'].label = "Tags :"
        self.fields['gender'].label = "Gender :"
        self.fields['last_date'].label = "Submission Deadline :"
        self.fields['company_name'].label = "Company Name :"
        self.fields['url'].label = "Website :"
        self.fields['category'].label = "Category :"
        self.fields['job_type'].label = "Job Type :"

        # Customize widgets (placeholders)
        self.fields['title'].widget.attrs.update({'placeholder': 'eg : Software Developer'})
        self.fields['location'].widget.attrs.update({'placeholder': 'eg : Karaikal, Puducherry'})
        self.fields['salary'].widget.attrs.update({'placeholder': '********'})
        self.fields['Vacancy'].widget.attrs.update({'placeholder': ''})
        self.fields['passedout'].widget.attrs.update({'placeholder': ''})
        self.fields['Experience'].widget.attrs.update({'placeholder': ''})
        self.fields['tags'].widget.attrs.update({'placeholder': 'eg: Python, JavaScript'})
        self.fields['gender'].widget.attrs.update({'placeholder': ''})
        self.fields['last_date'].widget.attrs.update({'placeholder': 'YYYY-MM-DD'})
        self.fields['company_name'].widget.attrs.update({'placeholder': 'Company Name'})
        self.fields['url'].widget.attrs.update({'placeholder': 'https://example.com'})
        
        # Refresh the queryset to ensure all categories are included
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].widget.attrs.update({
        'class': 'selectpicker border rounded',
        'data-style': 'btn-black',
        'data-width': '100%',
        'data-live-search': 'true',
        'title': 'Select Category',
    })

        
        # Keep job_type as dropdown
        self.fields['job_type'].widget = forms.Select(choices=JOB_TYPE)

    class Meta:
        model = Job
        fields = [
            "title",
            "location",
            "job_type",
            "category",
            "Vacancy",
            "passedout",
            "salary",
            "description",
            "Experience",
            "tags",
            "gender",
            "last_date",
            "company_name",
            "company_description",
            "url"
        ]

    def clean_job_type(self):
        job_type = self.cleaned_data.get('job_type')
        if not job_type:
            raise forms.ValidationError("Job Type is required")
        return job_type

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError("Category is required")
        return category

    def save(self, commit=True):
        job = super(JobForm, self).save(commit=False)
        if commit:
            job.save()
            self.save_m2m()  # Save tags (ManyToMany relationship)
        return job


class JobApplyForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['job', 'video']
        
    def __init__(self, *args, **kwargs):
        super(JobApplyForm, self).__init__(*args, **kwargs)
        # Make video field optional since we handle intro video separately
        self.fields['video'].required = False
        # Make job field hidden
        self.fields['job'].widget = forms.HiddenInput()
        # Add labels
        self.fields['job'].label = "Job Application"
        self.fields['video'].label = "Application Video"


class JobBookmarkForm(forms.ModelForm):
    class Meta:
        model = BookmarkJob
        fields = ['job']


class JobEditForm(forms.ModelForm):
    # Explicitly define the category field as ModelChoiceField
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a Category",
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super(JobEditForm, self).__init__(*args, **kwargs)
        # Refresh the queryset to ensure all categories are included
        self.fields['category'].queryset = Category.objects.all()
        
    class Meta:
        model = Job
        fields = [
            "title",
            "location",
            "job_type",
            "category",
            "Vacancy",
            "passedout",
            "salary",
            "description",
            "Experience",
            "tags",
            "gender",
            "last_date",
            "company_name",
            "company_description",
            "url"
        ]