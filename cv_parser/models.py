# from django.db import models
# from django.conf import settings
# from django.contrib.auth.models import User  # assuming you're using Django's default user system

# class CVParser(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     submission_datetime = models.DateTimeField(auto_now_add=True)
#     cv_file_name = models.CharField(max_length=255)
#     similarity_percent = models.FloatField()
#     top_qualified_users = models.TextField(help_text="Comma-separated user IDs or names")

#     def __str__(self):
#         return f"{self.user} - {self.cv_file_name}"

# class CVAnalysis(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     name = models.CharField(max_length=255)
#     email = models.EmailField()
#     linkedin_link = models.URLField(blank=True, null=True)
#     skills = models.TextField(help_text="Comma-separated or JSON-formatted skills")
#     language = models.CharField(max_length=100)
#     degree = models.CharField(max_length=100)
#     university = models.CharField(max_length=255)

#     def __str__(self):
#         return f"{self.name} ({self.user})"


# from django.db import models
# from django.conf import settings

# class CVParser(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     submission_datetime = models.DateTimeField(auto_now_add=True)
#     cv_file_name = models.CharField(max_length=255)
#     similarity_percent = models.FloatField()
#     top_qualified_users = models.TextField()

# class CVAnalysis(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     name = models.CharField(max_length=255)
#     #email = models.EmailField()
#     email = models.EmailField(blank=True, null=True)
#     linkedin_link = models.URLField(blank=True)
#     skills = models.TextField()
#     #language = models.TextField()
#     language = models.TextField(blank=True, null=True)
#     degree = models.TextField()
#     university = models.CharField(max_length=255)
#     status = models.CharField(max_length=50, default='Pending')









from django.db import models
from django.conf import settings

class CVParser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission_datetime = models.DateTimeField(auto_now_add=True)
    #cv_file_name = models.CharField(max_length=255)
    cv_file_name = models.CharField(max_length=255,default='unknown_cv.pdf')
    #similarity_percent = models.FloatField()
    similarity_percent = models.FloatField(default=0.0)
    #top_qualified_users = models.TextField()
    top_qualified_users = models.TextField(default='[]')  # default to an empty JSON array
class CVAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    name = models.CharField(max_length=255, default='Unknown')  # non-nullable, so we give a default
    email = models.EmailField(blank=True, null=True)             # optional
    linkedin_link = models.URLField(blank=True)                  # optional
    skills = models.TextField()                                  # required
    language = models.TextField(blank=True, null=True)           # optional
    degree = models.TextField(default='Unknown')                 # non-nullable, needs a default
    university = models.CharField(max_length=255, default='Unknown')  # non-nullable, needs a default
    status = models.CharField(max_length=50, default='Pending')  # default provided

