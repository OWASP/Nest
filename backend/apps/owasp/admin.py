"""OWASP app admin."""

from django.contrib import admin

from apps.owasp.models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_filter = ("level", "type")
    search_fields = ("name", "description")


admin.site.register(Project, ProjectAdmin)
