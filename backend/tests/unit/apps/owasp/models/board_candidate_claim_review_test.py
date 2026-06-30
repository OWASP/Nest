"""Tests for BoardCandidateClaimReview model."""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.github.models.user import User as GithubUser
from apps.nest.models.user import User
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_review import BoardCandidateClaimReview
from apps.owasp.models.board_of_directors import BoardOfDirectors


class TestBoardCandidateClaimReviewModel:
    """Tests for BoardCandidateClaimReview model."""

    def test_str_representation(self):
        """Test __str__ returns claim name and reviewer login."""
        claim = BoardCandidateClaim(name="Community Outreach")
        reviewer = User()
        reviewer.username = "alice"

        review = BoardCandidateClaimReview(status=BoardCandidateClaimReview.Status.APPROVED)
        review.claim = claim
        review.reviewer = reviewer

        assert str(review) == "Community Outreach - alice"

    def test_meta_options(self):
        """Test model meta options."""
        assert BoardCandidateClaimReview._meta.db_table == "owasp_board_candidate_claim_reviews"
        assert (
            BoardCandidateClaimReview._meta.verbose_name_plural == "Board Candidate Claim Reviews"
        )

    def test_meta_constraints(self):
        """Test model constraints are defined."""
        constraint_names = {c.name for c in BoardCandidateClaimReview._meta.constraints}

        assert "owasp_claim_reviewer_unique" in constraint_names

    def test_has_timestamp_fields(self):
        """Test model has timestamp fields from TimestampedModel."""
        assert hasattr(BoardCandidateClaimReview, "nest_created_at")
        assert hasattr(BoardCandidateClaimReview, "nest_updated_at")

    def test_notes_default_empty(self):
        """Test notes field defaults to empty string."""
        field = BoardCandidateClaimReview._meta.get_field("notes")

        assert field.default == ""
        assert field.blank

    def test_status_choices(self):
        """Test status choices are correctly defined."""
        assert BoardCandidateClaimReview.Status.APPROVED == "APPROVED"
        assert BoardCandidateClaimReview.Status.REJECTED == "REJECTED"

    def test_status_max_length(self):
        """Test status field max_length."""
        field = BoardCandidateClaimReview._meta.get_field("status")

        assert field.max_length == 8

    def _build_review(
        self, *, status=None, claim_status=None, reviewer_user=None, claim_board=None
    ):
        """Build a review with mocked claim and reviewer."""
        claim = BoardCandidateClaim(status=claim_status or BoardCandidateClaim.Status.SUBMITTED)
        claim.board = claim_board

        review = BoardCandidateClaimReview(
            status=status or BoardCandidateClaimReview.Status.APPROVED,
            notes="Some notes",
        )
        review.claim = claim
        review.reviewer = reviewer_user

        return review

    def test_clean_passes_for_claim_reviewer_role(self):
        """Test that clean passes when reviewer is a claim reviewer."""
        reviewer_user = User()
        board = BoardOfDirectors()
        board.get_candidate = MagicMock(return_value=None)

        with (
            patch.object(BoardOfDirectors, "reviewers") as mock_reviewers,
            patch.object(User, "github_user", new_callable=PropertyMock) as mock_github_user,
        ):
            mock_reviewers.filter.return_value.exists.return_value = True
            mock_github_user.return_value = GithubUser(login="alice")

            review = self._build_review(
                claim_status=BoardCandidateClaim.Status.SUBMITTED,
                reviewer_user=reviewer_user,
                claim_board=board,
            )

            review.clean()

    @pytest.mark.parametrize(
        "status",
        [
            BoardCandidateClaim.Status.DRAFT,
            BoardCandidateClaim.Status.APPROVED,
            BoardCandidateClaim.Status.REJECTED,
            BoardCandidateClaim.Status.DISCARDED,
            BoardCandidateClaim.Status.WITHDRAWN,
        ],
    )
    def test_clean_non_submitted_claim_raises(self, status):
        """Test that clean raises ValidationError when claim is not submitted."""
        reviewer_user = User()
        review = self._build_review(claim_status=status, reviewer_user=reviewer_user)

        with patch.object(User, "github_user") as mock_github_user:
            mock_github_user.login = "alice"
            with pytest.raises(ValidationError) as exc_info:
                review.clean()

        assert str(exc_info.value.messages[0]) == "Review can only be added to submitted claims."

    def test_clean_reviewer_without_reviewer_role_raises(self):
        """Test that clean raises ValidationError when reviewer lacks required roles."""
        reviewer_user = User()
        review = self._build_review(
            claim_status=BoardCandidateClaim.Status.SUBMITTED,
            reviewer_user=reviewer_user,
        )

        with patch.object(User, "github_user") as mock_github_user:
            mock_github_user.login = "alice"
            with pytest.raises(ValidationError) as exc_info:
                review.clean()

        assert str(exc_info.value.messages[0]) == "Only Claim Reviewers can review claims."

    def test_clean_candidate_reviewing_same_election_year_raises(self):
        """Test that clean raises ValidationError when reviewer is candidate in the same board."""
        reviewer_user = User()
        board = BoardOfDirectors()
        board.get_candidate = MagicMock(return_value=MagicMock())  # candidate found

        with (
            patch.object(BoardOfDirectors, "reviewers") as mock_reviewers,
            patch.object(User, "github_user") as mock_github_user,
        ):
            mock_reviewers.filter.return_value.exists.return_value = True
            mock_github_user.login = "alice"
            review = self._build_review(
                claim_status=BoardCandidateClaim.Status.SUBMITTED,
                reviewer_user=reviewer_user,
                claim_board=board,
            )

            with pytest.raises(ValidationError) as exc_info:
                review.clean()

            assert (
                str(exc_info.value.messages[0])
                == "A candidate cannot review claims in the same election year."
            )

            board.get_candidate.assert_called_once_with(login="alice")

    def test_clean_raises_validation_error_when_no_github_user(self):
        """Test that clean raises ValidationError when when reviewer has no linked github user."""
        reviewer_user = User()
        board = BoardOfDirectors()
        with patch.object(BoardOfDirectors, "reviewers") as mock_reviewers:
            mock_reviewers.filter.return_value.exists.return_value = True
            review = self._build_review(
                claim_status=BoardCandidateClaim.Status.SUBMITTED,
                reviewer_user=reviewer_user,
                claim_board=board,
            )
            with pytest.raises(ValidationError):
                review.clean()

    @patch.object(BoardCandidateClaimReview, "full_clean")
    @patch("apps.owasp.models.board_candidate_claim_review.TimestampedModel.save")
    def test_save_calls_full_clean(self, mock_super_save, mock_full_clean):
        """Test that save calls full_clean before saving."""
        review = BoardCandidateClaimReview(status=BoardCandidateClaimReview.Status.APPROVED)

        review.save()

        mock_full_clean.assert_called_once()
        mock_super_save.assert_called_once()
