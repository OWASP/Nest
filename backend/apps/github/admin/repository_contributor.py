"""GitHub app RepositoryContributor model admin."""

from django.contrib import admin

from apps.github.models.repository_contributor import RepositoryContributor


class RepositoryContributorAdmin(admin.ModelAdmin):
    """Admin for RepositoryContributor model."""

    autocomplete_fields = (
        "repository",
        "user",
    )
    search_fields = ("user__login", "user__name")


admin.site.register(RepositoryContributor, RepositoryContributorAdmin)
