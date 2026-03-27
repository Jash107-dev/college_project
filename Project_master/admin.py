from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'status', 'created_at')
    search_fields = ('title', 'student__username')
    list_filter = ('status', 'created_at')
