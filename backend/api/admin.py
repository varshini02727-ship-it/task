from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subject, Mark

# Creates a custom admin view for our User model.
class CustomUserAdmin(UserAdmin):
    # This adds our custom 'role' field to the user editing page in the admin panel.
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Custom Fields',
            {
                'fields': (
                    'role',
                ),
            },
        ),
    )

class MarkAdmin(admin.ModelAdmin):
    # Defines the columns to show in the list view for Marks.
    list_display = ('student', 'subject', 'score', 'grade')
    # Adds a filter sidebar.
    list_filter = ('subject', 'student')
    # Adds a search bar.
    search_fields = ('student__username', 'subject__name')

class SubjectAdmin(admin.ModelAdmin):
    # Defines the columns to show in the list view for Subjects.
    list_display = ('name', 'teacher')
    # Adds a search bar.
    search_fields = ('name', 'teacher__username')

# Registers our models with the admin site so they can be managed.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Mark, MarkAdmin)