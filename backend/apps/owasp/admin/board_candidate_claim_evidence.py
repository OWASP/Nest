"""BoardCandidateClaimEvidence admin configuration."""

from django.contrib import admin

from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence

from .mixins import GenericEntityAdminMixin


class BoardCandidateClaimEvidenceAdmin(GenericEntityAdminMixin, admin.ModelAdmin):
    """Admin for BoardCandidateClaimEvidence model."""

    list_filter = ("is_removed",)
    search_fields = ("name",)


admin.site.register(BoardCandidateClaimEvidence, BoardCandidateClaimEvidenceAdmin)
