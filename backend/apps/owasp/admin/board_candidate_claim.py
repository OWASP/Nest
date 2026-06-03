"""BoardCandidateClaim admin configuration."""

from django.contrib import admin

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim

from .mixins import GenericEntityAdminMixin


class BoardCandidateClaimAdmin(admin.ModelAdmin, GenericEntityAdminMixin):
    """Admin for BoardCandidateClaim model."""

    list_filter = ("status",)
    search_fields = ("title",)


admin.site.register(BoardCandidateClaim, BoardCandidateClaimAdmin)
