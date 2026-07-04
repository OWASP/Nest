"""BoardCandidateClaimReview admin configuration."""

from django.contrib import admin

from apps.owasp.models.board_candidate_claim_review import BoardCandidateClaimReview

from .mixins import GenericEntityAdminMixin


class BoardCandidateClaimReviewAdmin(admin.ModelAdmin, GenericEntityAdminMixin):
    """Admin for BoardCandidateClaimReview model."""

    list_filter = ("status",)
    search_fields = ("notes",)


admin.site.register(BoardCandidateClaimReview, BoardCandidateClaimReviewAdmin)
