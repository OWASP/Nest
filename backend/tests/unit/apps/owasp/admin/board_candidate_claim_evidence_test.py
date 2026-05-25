"""Tests for BoardCandidateClaimEvidenceAdmin."""

from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.board_candidate_claim_evidence import BoardCandidateClaimEvidenceAdmin
from apps.owasp.admin.mixins import GenericEntityAdminMixin
from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence


class TestBoardCandidateClaimEvidenceAdmin:
    """Tests for BoardCandidateClaimEvidenceAdmin."""

    def test_list_filter(self):
        """Test list_filter fields."""
        admin_instance = BoardCandidateClaimEvidenceAdmin(BoardCandidateClaimEvidence, AdminSite())

        assert admin_instance.list_filter == ("is_removed",)

    def test_search_fields(self):
        """Test search_fields."""
        admin_instance = BoardCandidateClaimEvidenceAdmin(BoardCandidateClaimEvidence, AdminSite())

        assert admin_instance.search_fields == ("title",)

    def test_inherits_generic_entity_admin_mixin(self):
        """Test admin inherits from GenericEntityAdminMixin."""
        assert issubclass(BoardCandidateClaimEvidenceAdmin, GenericEntityAdminMixin)
        assert issubclass(BoardCandidateClaimEvidenceAdmin, admin.ModelAdmin)
