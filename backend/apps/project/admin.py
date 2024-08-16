"""Project app admin."""

from django.contrib import admin

from apps.project.models import Project

admin.site.register(Project)
