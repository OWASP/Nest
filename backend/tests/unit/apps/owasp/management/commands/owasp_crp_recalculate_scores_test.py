from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

COMMAND_PATH = "apps.owasp.management.commands.owasp_crp_recalculate_scores"


class TestOwaspCrpRecalculateScores:
    """Test suite for the owasp_crp_recalculate_scores management command."""

    @patch(f"{COMMAND_PATH}.ContributionScoreCalculator")
    def test_handle_success(self, mock_calculator_class):
        """Test successful score recalculation with no failures."""
        mock_calculator = MagicMock()
        mock_calculator.recalculate_all.return_value = {
            "total": 10,
            "created": 3,
            "updated": 7,
            "failed_count": 0,
        }
        mock_calculator_class.return_value = mock_calculator

        out = StringIO()
        call_command("owasp_crp_recalculate_scores", stdout=out)

        mock_calculator_class.assert_called_once()
        mock_calculator.recalculate_all.assert_called_once()

        output = out.getvalue()
        assert "Starting score recalculation for all users..." in output
        assert "Score recalculation complete:" in output
        assert "- Total users: 10" in output
        assert "- Created: 3" in output
        assert "- Updated: 7" in output
        assert "- Failed: 0" in output

    @patch(f"{COMMAND_PATH}.ContributionScoreCalculator")
    def test_handle_with_failures(self, mock_calculator_class):
        """Test score recalculation when certificate issuance failures occur."""
        mock_calculator = MagicMock()
        mock_calculator.recalculate_all.return_value = {
            "total": 5,
            "created": 1,
            "updated": 2,
            "failed_count": 2,
            "failures": [("alice", "Certificate error"), ("bob", "Network error")],
        }
        mock_calculator_class.return_value = mock_calculator

        out = StringIO()
        with pytest.raises(
            CommandError, match=r"Failed to issue certificates for 2 user\(s\)"
        ):
            call_command("owasp_crp_recalculate_scores", stdout=out)

        output = out.getvalue()
        assert "Failed to issue certificates for: alice, bob" in output

    @patch(f"{COMMAND_PATH}.ContributionScoreCalculator")
    def test_handle_with_failures_no_failures_list(self, mock_calculator_class):
        """Test score recalculation when failed_count > 0 but failures key is missing."""
        mock_calculator = MagicMock()
        mock_calculator.recalculate_all.return_value = {
            "total": 2,
            "created": 0,
            "updated": 1,
            "failed_count": 1,
        }
        mock_calculator_class.return_value = mock_calculator

        out = StringIO()
        with pytest.raises(
            CommandError, match=r"Failed to issue certificates for 1 user\(s\)"
        ):
            call_command("owasp_crp_recalculate_scores", stdout=out)

        output = out.getvalue()
        assert "Failed to issue certificates for: " in output
