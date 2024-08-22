"""OWASP app admin."""

from django.contrib import admin

from apps.owasp.models import Chapter, Committee, Event, Project


class ChapterAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    list_filter = ("country", "region")
    search_fields = ("name",)


class CommetteeAdmin(admin.ModelAdmin):
    search_fields = ("name",)


class EventAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "level")
    list_filter = ("level", "type")
    search_fields = ("name", "description")


admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Committee, CommetteeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Project, ProjectAdmin)
