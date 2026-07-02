"""Tests for BoardCandidateClaimReviewAdmin."""

from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.board_candidate_claim_review import BoardCandidateClaimReviewAdmin
from apps.owasp.admin.mixins import GenericEntityAdminMixin
from apps.owasp.models.board_candidate_claim_review import BoardCandidateClaimReview


class TestBoardCandidateClaimReviewAdmin:
    """Tests for BoardCandidateClaimReviewAdmin."""

    def test_list_filter(self):
        """Test list_filter includes status."""
        admin_instance = BoardCandidateClaimReviewAdmin(BoardCandidateClaimReview, AdminSite())

        assert admin_instance.list_filter == ("status",)

    def test_search_fields(self):
        """Test search_fields includes notes."""
        admin_instance = BoardCandidateClaimReviewAdmin(BoardCandidateClaimReview, AdminSite())

        assert admin_instance.search_fields == ("notes",)

    def test_inherits_generic_entity_admin_mixin(self):
        """Test admin inherits from GenericEntityAdminMixin."""
        assert issubclass(BoardCandidateClaimReviewAdmin, GenericEntityAdminMixin)
        assert issubclass(BoardCandidateClaimReviewAdmin, admin.ModelAdmin)
