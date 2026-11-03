"""GitHub app Milestone model admin."""

from django.contrib import admin

from apps.github.models.milestone import Milestone


class MilestoneAdmin(admin.ModelAdmin):
    """Admin for Milestone model."""

    autocomplete_fields = (
        "author",
        "labels",
        "repository",
    )
    search_fields = (
        "body",
        "title",
    )


admin.site.register(Milestone, MilestoneAdmin)
