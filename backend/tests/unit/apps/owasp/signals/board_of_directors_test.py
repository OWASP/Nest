"""Tests for BoardOfDirectors signal handler."""

from unittest.mock import MagicMock, patch

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.signals.board_of_directors import (
    board_post_save_re_evaluate_claims,
)


class TestBoardPostSaveReEvaluateClaims:
    """Tests for board_post_save_re_evaluate_claims signal."""

    @patch("apps.owasp.signals.board_of_directors.logger")
    @patch("apps.owasp.signals.board_of_directors.BoardCandidateClaim")
    def test_approves_claims_when_threshold_met(self, mock_claim_model, mock_logger):
        mock_claim_model.Status = BoardCandidateClaim.Status
        instance = MagicMock(spec=BoardOfDirectors)
        instance.reviews_threshold = 2
        instance.year = 2025

        claim_a = MagicMock(spec=BoardCandidateClaim)
        claim_a.status = BoardCandidateClaim.Status.SUBMITTED
        claim_a.reviews.filter.return_value.count.return_value = 3

        claim_b = MagicMock(spec=BoardCandidateClaim)
        claim_b.status = BoardCandidateClaim.Status.SUBMITTED
        claim_b.reviews.filter.return_value.count.return_value = 1

        instance.claims.filter.return_value = [claim_a, claim_b]

        board_post_save_re_evaluate_claims(sender=None, instance=instance)

        assert claim_a.status == BoardCandidateClaim.Status.APPROVED
        assert claim_a.is_locked is True
        assert claim_b.status == BoardCandidateClaim.Status.SUBMITTED
        mock_claim_model.objects.bulk_update.assert_called_once_with(
            [claim_a], ["is_locked", "status"]
        )
        mock_logger.info.assert_called_once_with(
            "Approved %d claims after threshold change on board %d.",
            1,
            2025,
        )

    @patch("apps.owasp.signals.board_of_directors.logger")
    @patch("apps.owasp.signals.board_of_directors.BoardCandidateClaim")
    def test_approves_no_claims_when_threshold_not_met(self, mock_claim_model, mock_logger):
        mock_claim_model.Status = BoardCandidateClaim.Status
        instance = MagicMock(spec=BoardOfDirectors)
        instance.reviews_threshold = 5
        instance.year = 2025

        claim_a = MagicMock(spec=BoardCandidateClaim)
        claim_a.status = BoardCandidateClaim.Status.SUBMITTED
        claim_a.reviews.filter.return_value.count.return_value = 3

        instance.claims.filter.return_value = [claim_a]

        board_post_save_re_evaluate_claims(sender=None, instance=instance)

        mock_claim_model.objects.bulk_update.assert_not_called()
        mock_logger.info.assert_not_called()

    @patch("apps.owasp.signals.board_of_directors.logger")
    @patch("apps.owasp.signals.board_of_directors.BoardCandidateClaim")
    def test_approves_all_eligible_claims(self, mock_claim_model, mock_logger):
        mock_claim_model.Status = BoardCandidateClaim.Status
        instance = MagicMock(spec=BoardOfDirectors)
        instance.reviews_threshold = 1
        instance.year = 2025

        claim_a = MagicMock(spec=BoardCandidateClaim)
        claim_a.status = BoardCandidateClaim.Status.SUBMITTED
        claim_a.reviews.filter.return_value.count.return_value = 1

        claim_b = MagicMock(spec=BoardCandidateClaim)
        claim_b.status = BoardCandidateClaim.Status.SUBMITTED
        claim_b.reviews.filter.return_value.count.return_value = 2

        instance.claims.filter.return_value = [claim_a, claim_b]

        board_post_save_re_evaluate_claims(sender=None, instance=instance)

        assert claim_a.status == BoardCandidateClaim.Status.APPROVED
        assert claim_a.is_locked is True
        assert claim_b.status == BoardCandidateClaim.Status.APPROVED
        assert claim_b.is_locked is True
        mock_claim_model.objects.bulk_update.assert_called_once_with(
            [claim_a, claim_b], ["is_locked", "status"]
        )
        mock_logger.info.assert_called_once()

    @patch("apps.owasp.signals.board_of_directors.BoardCandidateClaim")
    def test_skips_when_threshold_not_in_update_fields(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        instance = MagicMock(spec=BoardOfDirectors)
        instance.claims.filter.return_value = [MagicMock()]

        board_post_save_re_evaluate_claims(sender=None, instance=instance, update_fields=["year"])

        instance.claims.filter.assert_not_called()
        mock_claim_model.objects.bulk_update.assert_not_called()

    def test_skips_for_new_board(self):
        instance = MagicMock(spec=BoardOfDirectors)

        board_post_save_re_evaluate_claims(sender=None, instance=instance, created=True)

        instance.claims.filter.assert_not_called()

    @patch("apps.owasp.signals.board_of_directors.BoardCandidateClaim")
    def test_runs_when_threshold_in_update_fields(self, mock_claim_model):
        mock_claim_model.Status = BoardCandidateClaim.Status
        instance = MagicMock(spec=BoardOfDirectors)
        instance.reviews_threshold = 2
        instance.year = 2025
        instance.claims.filter.return_value = []

        board_post_save_re_evaluate_claims(
            sender=None, instance=instance, update_fields=["reviews_threshold"]
        )

        instance.claims.filter.assert_called_once()
        mock_claim_model.objects.bulk_update.assert_not_called()
