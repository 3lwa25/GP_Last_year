# # cv_parser/admin.py
# from django.contrib import admin
# from .models import CVParser, CVAnalysis

# # Custom Admin for CVParser
# class CVParserAdmin(admin.ModelAdmin):
#     list_display = ('user', 'cv_file_name', 'similarity_percent', 'submission_datetime', 'top_qualified_users')
#     search_fields = ('cv_file_name', 'user__username')
#     list_filter = ('submission_datetime',)
#     ordering = ('-submission_datetime',)
#     date_hierarchy = 'submission_datetime'
    
#     # To customize the form view (e.g., add more fields in the form)
#     fieldsets = (
#         (None, {
#             'fields': ('user', 'cv_file_name', 'similarity_percent', 'top_qualified_users')
#         }),
#         ('Time Information', {
#             'fields': ('submission_datetime',),
#             'classes': ('collapse',),
#         }),
#     )

# # Custom Admin for CVAnalysis
# class CVAnalysisAdmin(admin.ModelAdmin):
#     list_display = ('user', 'name', 'email', 'language', 'degree', 'university', 'linkedin_link')
#     search_fields = ('name', 'user__username', 'email', 'degree', 'university')
#     list_filter = ('language', 'degree')
#     ordering = ('name',)
    
#     # Customizing the fields displayed in the form
#     fieldsets = (
#         (None, {
#             'fields': ('user', 'name', 'email', 'linkedin_link', 'skills', 'language', 'degree', 'university')
#         }),
#     )

# def mark_as_reviewed(self, request, queryset):
#     queryset.update(status='Reviewed')
# mark_as_reviewed.short_description = 'Mark selected as reviewed'

# actions = [mark_as_reviewed]

from django.contrib import admin
from .models import CVParser, CVAnalysis


@admin.register(CVParser)
class CVParserAdmin(admin.ModelAdmin):
    list_display = ('user', 'cv_file_name', 'similarity_percent', 'submission_datetime', 'top_qualified_users')
    search_fields = ('cv_file_name', 'user__username')
    list_filter = ('submission_datetime',)
    ordering = ('-submission_datetime',)
    date_hierarchy = 'submission_datetime'

    readonly_fields = ('submission_datetime',)

    fieldsets = (
        (None, {
            'fields': ('user', 'cv_file_name', 'similarity_percent', 'top_qualified_users')
        }),
        ('Timestamp Info', {
            'fields': ('submission_datetime',),
            'classes': ('collapse',),
        }),
    )


@admin.register(CVAnalysis)
class CVAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'language', 'degree', 'university', 'linkedin_link')
    search_fields = ('name', 'user__username', 'email', 'degree', 'university')
    list_filter = ('language', 'degree')
    ordering = ('name',)

    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'email', 'linkedin_link', 'skills', 'language', 'degree', 'university')
        }),
    )

    # Optional action
    @admin.action(description='Mark selected as reviewed')
    def mark_as_reviewed(self, request, queryset):
        queryset.update(status='Reviewed')

    actions = ['mark_as_reviewed']  # Optional if 'status' field exists