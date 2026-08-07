"""Django admin configuration for BoardCandidateProfile model."""

from django.contrib import admin
from django.db import models

from apps.owasp.models.board_candidate_profile import BoardCandidateProfile


class BoardCandidateProfileAdmin(admin.ModelAdmin):
    """Admin for BoardCandidateProfile model."""

    autocomplete_fields = ("candidate",)
    list_display = (
        "__str__",
        "nest_created_at",
        "nest_updated_at",
    )
    search_fields = (
        "candidate__member_name",
        "candidate__member__login",
        "raw_markdown",
    )
    readonly_fields = (
        "nest_created_at",
        "nest_updated_at",
    )

    def get_queryset(self, request) -> models.QuerySet:
        """Retrieve optimized queryset with related candidate.

        Args:
            request: The HTTP request object.

        Returns:
            QuerySet: BoardCandidateProfile queryset with prefetched candidate.

        """
        return super().get_queryset(request).select_related("candidate__member")


admin.site.register(BoardCandidateProfile, BoardCandidateProfileAdmin)
