"""GitHub app Commit model admin."""

from django.contrib import admin

from apps.github.models.commit import Commit


class CommitAdmin(admin.ModelAdmin):
    """Admin for Commit model."""

    autocomplete_fields = (
        "author",
        "committer",
        "repository",
    )
    list_display = (
        "sha",
        "repository",
        "author",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "sha",
        "message",
        "node_id",
        "repository__name",
        "author__login",
    )


admin.site.register(Commit, CommitAdmin)
