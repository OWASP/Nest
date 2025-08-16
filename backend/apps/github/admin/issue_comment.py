"""GitHub app Issue model admin."""

from django.contrib import admin

from apps.github.models import IssueComment


class IssueCommentAdmin(admin.ModelAdmin):
    """Admin for IssueComment model."""

    list_display = (
        "body",
        "issue",
        "author",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("body", "issue__title")


admin.site.register(IssueComment, IssueCommentAdmin)
