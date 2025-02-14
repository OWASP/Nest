"""Core app admin."""

#!/usr/bin/env python3
from django.contrib import admin

from apps.core.models.prompt import Prompt


class PromptAdmin(admin.ModelAdmin):
    search_fields = ("name",)


admin.site.register(Prompt, PromptAdmin)
