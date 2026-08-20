"""Tests for BoardCandidateProfile GraphQL queries."""

from unittest.mock import MagicMock, patch

from apps.owasp.api.internal.queries.board_candidate_profile import BoardCandidateProfileQuery
from apps.owasp.models.board_candidate_profile import BoardCandidateProfile
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.entity_member import EntityMember


class TestBoardCandidateProfileQuery:
    """Tests for board_candidate_profile query."""

    @patch("apps.owasp.api.internal.queries.board_candidate_profile.ContentType")
    @patch("apps.owasp.api.internal.queries.board_candidate_profile.BoardOfDirectors")
    @patch("apps.owasp.api.internal.queries.board_candidate_profile.BoardCandidateProfile")
    def test_returns_profile_when_found(self, mock_profile_model, mock_board_model, mock_ct):
        mock_profile_model.DoesNotExist = BoardCandidateProfile.DoesNotExist
        mock_board_model.DoesNotExist = BoardOfDirectors.DoesNotExist

        board = MagicMock()
        board.id = 42
        mock_board_model.objects.get.return_value = board

        content_type = MagicMock()
        mock_ct.objects.get_for_model.return_value = content_type

        profile = MagicMock()
        mock_qs = MagicMock()
        mock_qs.get.return_value = profile
        mock_profile_model.objects.select_related.return_value = mock_qs

        query = BoardCandidateProfileQuery()
        info = MagicMock()
        result = query.board_candidate_profile(info, login="alice", year=2025)

        mock_board_model.objects.get.assert_called_once_with(year=2025)
        mock_ct.objects.get_for_model.assert_called_once_with(mock_board_model)
        mock_profile_model.objects.select_related.assert_called_once_with("candidate__member")
        mock_qs.get.assert_called_once_with(
            candidate__member__login="alice",
            candidate__entity_type=content_type,
            candidate__entity_id=42,
            candidate__role=EntityMember.Role.CANDIDATE,
            candidate__is_active=True,
            candidate__is_reviewed=True,
        )
        assert result == profile

    @patch("apps.owasp.api.internal.queries.board_candidate_profile.ContentType")
    @patch("apps.owasp.api.internal.queries.board_candidate_profile.BoardOfDirectors")
    @patch("apps.owasp.api.internal.queries.board_candidate_profile.BoardCandidateProfile")
    def test_returns_none_when_board_missing(self, mock_profile_model, mock_board_model, mock_ct):
        mock_profile_model.DoesNotExist = BoardCandidateProfile.DoesNotExist
        mock_board_model.DoesNotExist = BoardOfDirectors.DoesNotExist
        mock_board_model.objects.get.side_effect = BoardOfDirectors.DoesNotExist

        query = BoardCandidateProfileQuery()
        info = MagicMock()
        result = query.board_candidate_profile(info, login="alice", year=2099)

        assert result is None

    @patch("apps.owasp.api.internal.queries.board_candidate_profile.ContentType")
    @patch("apps.owasp.api.internal.queries.board_candidate_profile.BoardOfDirectors")
    @patch("apps.owasp.api.internal.queries.board_candidate_profile.BoardCandidateProfile")
    def test_returns_none_when_profile_missing(
        self, mock_profile_model, mock_board_model, mock_ct
    ):
        mock_profile_model.DoesNotExist = BoardCandidateProfile.DoesNotExist
        mock_board_model.DoesNotExist = BoardOfDirectors.DoesNotExist

        board = MagicMock()
        board.id = 7
        mock_board_model.objects.get.return_value = board
        mock_ct.objects.get_for_model.return_value = MagicMock()

        mock_qs = MagicMock()
        mock_qs.get.side_effect = BoardCandidateProfile.DoesNotExist
        mock_profile_model.objects.select_related.return_value = mock_qs

        query = BoardCandidateProfileQuery()
        info = MagicMock()
        result = query.board_candidate_profile(info, login="unknown", year=2025)

        assert result is None

    @patch("apps.owasp.api.internal.queries.board_candidate_profile.ContentType")
    @patch("apps.owasp.api.internal.queries.board_candidate_profile.BoardOfDirectors")
    @patch("apps.owasp.api.internal.queries.board_candidate_profile.BoardCandidateProfile")
    def test_inactive_candidate_returns_none(self, mock_profile_model, mock_board_model, mock_ct):
        mock_profile_model.DoesNotExist = BoardCandidateProfile.DoesNotExist
        mock_board_model.DoesNotExist = BoardOfDirectors.DoesNotExist

        board = MagicMock()
        board.id = 1
        mock_board_model.objects.get.return_value = board
        mock_ct.objects.get_for_model.return_value = MagicMock()

        mock_qs = MagicMock()
        mock_qs.get.side_effect = BoardCandidateProfile.DoesNotExist
        mock_profile_model.objects.select_related.return_value = mock_qs

        query = BoardCandidateProfileQuery()
        info = MagicMock()
        result = query.board_candidate_profile(info, login="inactive", year=2025)

        _, kwargs = mock_qs.get.call_args
        assert kwargs["candidate__is_active"]
        assert kwargs["candidate__is_reviewed"]
        assert kwargs["candidate__role"] == EntityMember.Role.CANDIDATE
        assert result is None
