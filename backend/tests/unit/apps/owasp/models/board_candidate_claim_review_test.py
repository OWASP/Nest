"""Tests for BoardCandidateClaimReview model."""

from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.github.models.user import User
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_review import BoardCandidateClaimReview
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.entity_member import EntityMember


class TestBoardCandidateClaimReviewModel:
    """Tests for BoardCandidateClaimReview model."""

    def test_str_representation(self):
        """Test __str__ returns claim name and reviewer login."""
        claim = BoardCandidateClaim(name="Community Outreach")
        reviewer_user = User()
        reviewer_user.login = "alice"
        reviewer = EntityMember()
        reviewer.member = reviewer_user

        review = BoardCandidateClaimReview(decision=BoardCandidateClaimReview.Decision.APPROVED)
        review.claim = claim
        review.reviewer = reviewer

        assert str(review) == "Community Outreach - alice"

    def test_meta_options(self):
        """Test model meta options."""
        assert BoardCandidateClaimReview._meta.db_table == "owasp_board_candidate_claim_review"
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

    def test_decision_choices(self):
        """Test decision choices are correctly defined."""
        assert BoardCandidateClaimReview.Decision.APPROVED == "APPROVED"
        assert BoardCandidateClaimReview.Decision.REJECTED == "REJECTED"

    def test_decision_max_length(self):
        """Test decision field max_length."""
        field = BoardCandidateClaimReview._meta.get_field("decision")

        assert field.max_length == 8

    def test_notes_default_empty(self):
        """Test notes field defaults to empty string."""
        field = BoardCandidateClaimReview._meta.get_field("notes")

        assert field.default == ""
        assert field.blank

    def _build_review(
        self, *, decision=None, claim_status=None, reviewer_user=None, claim_board=None
    ):
        """Build a review with mocked claim and reviewer relations."""
        claim = BoardCandidateClaim(status=claim_status or BoardCandidateClaim.Status.SUBMITTED)
        claim.board = claim_board
        reviewer = EntityMember()
        reviewer.member = reviewer_user

        review = BoardCandidateClaimReview(
            decision=decision or BoardCandidateClaimReview.Decision.APPROVED,
            notes="Some notes",
        )
        review.claim = claim
        review.reviewer = reviewer

        return review

    def test_clean_passes_for_submitted_claim_with_valid_reviewer(self):
        """Test that clean passes when claim is submitted and reviewer is staff."""
        reviewer_user = User()
        reviewer_user.is_owasp_staff = True
        reviewer_user.is_claim_reviewer = False
        review = self._build_review(
            claim_status=BoardCandidateClaim.Status.SUBMITTED,
            reviewer_user=reviewer_user,
            claim_board=None,
        )

        review.clean()

    def test_clean_passes_for_claim_reviewer_role(self):
        """Test that clean passes when reviewer is a claim reviewer (not staff)."""
        reviewer_user = User()
        reviewer_user.is_owasp_staff = False
        reviewer_user.is_claim_reviewer = True
        review = self._build_review(
            claim_status=BoardCandidateClaim.Status.SUBMITTED,
            reviewer_user=reviewer_user,
            claim_board=None,
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
        reviewer_user.is_owasp_staff = True
        reviewer_user.is_claim_reviewer = False
        review = self._build_review(claim_status=status, reviewer_user=reviewer_user)

        with pytest.raises(ValidationError) as exc_info:
            review.clean()

        assert str(exc_info.value.messages[0]) == "Review can only be added to submitted claims."

    def test_clean_no_reviewer_member_raises(self):
        """Test that clean raises ValidationError when reviewer has no linked member."""
        review = self._build_review(
            claim_status=BoardCandidateClaim.Status.SUBMITTED,
            reviewer_user=None,
        )

        with pytest.raises(ValidationError) as exc_info:
            review.clean()

        assert (
            str(exc_info.value.messages[0])
            == "Only OWASP Staff or Claim Reviewers can review claims."
        )

    def test_clean_reviewer_without_staff_or_reviewer_role_raises(self):
        """Test that clean raises ValidationError when reviewer lacks required roles."""
        reviewer_user = User()
        reviewer_user.is_owasp_staff = False
        reviewer_user.is_claim_reviewer = False
        review = self._build_review(
            claim_status=BoardCandidateClaim.Status.SUBMITTED,
            reviewer_user=reviewer_user,
        )

        with pytest.raises(ValidationError) as exc_info:
            review.clean()

        assert (
            str(exc_info.value.messages[0])
            == "Only OWASP Staff or Claim Reviewers can review claims."
        )

    def test_clean_candidate_reviewing_same_election_year_raises(self):
        """Test that clean raises ValidationError when reviewer is candidate in the same board."""
        reviewer_user = User()
        reviewer_user.is_owasp_staff = True
        reviewer_user.is_claim_reviewer = False
        reviewer_user.login = "alice"
        board = BoardOfDirectors()
        board.get_candidate = MagicMock(return_value=MagicMock())  # candidate found

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

    def test_clean_passes_when_reviewer_not_a_candidate_on_board(self):
        """Test that clean passes when reviewer is staff and not a candidate on the board."""
        reviewer_user = User()
        reviewer_user.is_owasp_staff = True
        reviewer_user.is_claim_reviewer = False
        reviewer_user.login = "bob"
        board = BoardOfDirectors()
        board.get_candidate = MagicMock(return_value=None)  # not a candidate

        review = self._build_review(
            claim_status=BoardCandidateClaim.Status.SUBMITTED,
            reviewer_user=reviewer_user,
            claim_board=board,
        )

        review.clean()

        board.get_candidate.assert_called_once_with(login="bob")

    def test_clean_skips_candidate_check_when_no_board(self):
        """Test that clean skips the candidate-on-board check when claim has no board."""
        reviewer_user = User()
        reviewer_user.is_owasp_staff = True
        reviewer_user.is_claim_reviewer = False
        reviewer_user.login = "carol"
        review = self._build_review(
            claim_status=BoardCandidateClaim.Status.SUBMITTED,
            reviewer_user=reviewer_user,
            claim_board=None,
        )

        review.clean()

    @patch.object(BoardCandidateClaimReview, "full_clean")
    @patch("apps.owasp.models.board_candidate_claim_review.TimestampedModel.save")
    def test_save_calls_full_clean(self, mock_super_save, mock_full_clean):
        """Test that save calls full_clean before saving."""
        review = BoardCandidateClaimReview(decision=BoardCandidateClaimReview.Decision.APPROVED)

        review.save()

        mock_full_clean.assert_called_once()
        mock_super_save.assert_called_once()
