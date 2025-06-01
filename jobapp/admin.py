# from django.contrib import admin
# from .models import *
# from .models import Category


# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')
#     list_filter = ('name',)
#     search_fields = ('name', 'description')

# admin.site.register(Category, CategoryAdmin)
# # admin.site.register(Category)

# class ApplicantAdmin(admin.ModelAdmin):
#     list_display = ('job','user','timestamp')
    
# admin.site.register(Applicant,ApplicantAdmin)

# class JobAdmin(admin.ModelAdmin):
#     list_display = ('title','category','job_type','timestamp')
#     list_filter = ('category', 'job_type', 'is_published', 'is_closed')
#     search_fields = ('title', 'description', 'company_name')

# admin.site.register(Job, JobAdmin)

# class BookmarkJobAdmin(admin.ModelAdmin):
#     list_display = ('job','user','timestamp')
# admin.site.register(BookmarkJob,BookmarkJobAdmin)



from django.contrib import admin
from .models import Contact, Category, Job, Applicant, BookmarkJob, Video

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'category', 'job_type', 'is_published', 'is_closed')
    list_filter = ('category', 'job_type', 'is_published', 'is_closed')
    search_fields = ('title', 'company_name')

admin.site.register(Contact)
admin.site.register(Applicant)
admin.site.register(BookmarkJob)
admin.site.register(Video)