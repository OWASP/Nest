"""Tests for BoardCandidateProfile admin."""

from unittest import mock
from unittest.mock import MagicMock, Mock

from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.board_candidate_profile import BoardCandidateProfileAdmin
from apps.owasp.models.board_candidate_profile import BoardCandidateProfile


class TestBoardCandidateProfileAdmin:
    """Tests for BoardCandidateProfileAdmin."""

    def test_list_display(self) -> None:
        """Test list_display is configured properly."""
        admin = BoardCandidateProfileAdmin(BoardCandidateProfile, AdminSite())

        expected_fields = (
            "__str__",
            "nest_created_at",
            "nest_updated_at",
        )
        assert admin.list_display == expected_fields

    def test_search_fields(self) -> None:
        """Test search_fields is configured properly."""
        admin = BoardCandidateProfileAdmin(BoardCandidateProfile, AdminSite())

        expected_search = (
            "candidate__member_name",
            "candidate__member__login",
            "raw_markdown",
        )
        assert admin.search_fields == expected_search

    def test_readonly_fields(self) -> None:
        """Test readonly_fields is configured properly."""
        admin = BoardCandidateProfileAdmin(BoardCandidateProfile, AdminSite())

        expected_readonly = (
            "nest_created_at",
            "nest_updated_at",
        )
        assert admin.readonly_fields == expected_readonly

    def test_get_queryset(self) -> None:
        """Test get_queryset applies select_related for candidate."""
        admin = BoardCandidateProfileAdmin(BoardCandidateProfile, AdminSite())
        mock_request = Mock()

        admin_queryset = MagicMock()
        result_queryset = MagicMock()
        admin_queryset.select_related.return_value = result_queryset

        with mock.patch.object(
            admin.__class__.__bases__[0], "get_queryset", return_value=admin_queryset
        ):
            result = admin.get_queryset(mock_request)

            admin_queryset.select_related.assert_called_once_with("candidate__member")
            assert result == result_queryset
