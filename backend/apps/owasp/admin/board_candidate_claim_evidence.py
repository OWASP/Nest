"""BoardCandidateClaimEvidence admin configuration."""

from django.contrib import admin

from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence

from .mixins import GenericEntityAdminMixin


class BoardCandidateClaimEvidenceAdmin(admin.ModelAdmin, GenericEntityAdminMixin):
    """Admin for BoardCandidateClaim model."""

    list_filter = ("is_removed",)
    search_fields = ("title",)


admin.site.register(BoardCandidateClaimEvidence, BoardCandidateClaimEvidenceAdmin)
