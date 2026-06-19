"""Tests for BoardCandidateClaimAdmin."""

from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.board_candidate_claim import BoardCandidateClaimAdmin
from apps.owasp.admin.mixins import GenericEntityAdminMixin
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


class TestBoardCandidateClaimAdmin:
    """Tests for BoardCandidateClaimAdmin."""

    def test_list_filter(self):
        """Test list_filter includes status."""
        admin_instance = BoardCandidateClaimAdmin(BoardCandidateClaim, AdminSite())

        assert admin_instance.list_filter == ("status",)

    def test_search_fields(self):
        """Test search_fields includes name."""
        admin_instance = BoardCandidateClaimAdmin(BoardCandidateClaim, AdminSite())

        assert admin_instance.search_fields == ("name",)

    def test_inherits_generic_entity_admin_mixin(self):
        """Test admin inherits from GenericEntityAdminMixin."""
        assert issubclass(BoardCandidateClaimAdmin, GenericEntityAdminMixin)
        assert issubclass(BoardCandidateClaimAdmin, admin.ModelAdmin)
