"""Mentorship app admin"""

import algoliasearch.search.client
from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.mentorship.models.mentor import Mentor
import django.contrib.auth.models


class MentorAdmin(admin.ModelAdmin):
    search_fields = (
        "user",
        "years_of_experience",
        "domain",
    )


admin.site.register(Mentor, MentorAdmin)
