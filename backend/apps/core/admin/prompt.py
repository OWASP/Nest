"""Core app admin."""

from django.contrib import admin

from apps.core.models.prompt import Prompt


class PromptAdmin(admin.ModelAdmin):
    """Admin for Prompt model."""

    search_fields = ("name",)


admin.site.register(Prompt, PromptAdmin)
