import io
from datetime import UTC, datetime
from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_create_member_snapshot import Command


class TestOwaspCreateMemberSnapshotCommand:
    @pytest.fixture
    def command(self):
        return Command()

    def test_parse_date_valid(self, command):
        result = command.parse_date("2025-01-15", datetime(2025, 1, 1, tzinfo=UTC))

        assert result == datetime(2025, 1, 15, tzinfo=UTC)

    def test_parse_date_none_returns_default(self, command):
        default = datetime(2025, 2, 1, tzinfo=UTC)
        result = command.parse_date(None, default)

        assert result == default

    def test_parse_date_invalid_format(self, command):
        err = io.StringIO()
        command.stderr = err

        with pytest.raises(ValueError, match=r"time data .* does not match format"):
            command.parse_date("invalid-date", datetime.now(UTC))

        error_output = err.getvalue()
        assert "Invalid date format" in error_output

    def test_generate_heatmap_data(self, command):
        # Mock contributions with different dates
        mock_commit_1 = mock.Mock()
        mock_commit_1.created_at.date.return_value.isoformat.return_value = "2025-01-15"

        mock_commit_2 = mock.Mock()
        mock_commit_2.created_at.date.return_value.isoformat.return_value = "2025-01-15"

        mock_pr = mock.Mock()
        mock_pr.created_at.date.return_value.isoformat.return_value = "2025-01-16"

        mock_issue = mock.Mock()
        mock_issue.created_at.date.return_value.isoformat.return_value = "2025-01-15"

        # Call the actual method
        result = command.generate_heatmap_data(
            [mock_commit_1, mock_commit_2],
            [mock_pr],
            [mock_issue],
        )

        assert result == {"2025-01-15": 3, "2025-01-16": 1}

    def test_generate_heatmap_data_empty_contributions(self, command):
        result = command.generate_heatmap_data([], [], [])

        assert result == {}

    def test_generate_heatmap_data_single_date(self, command):
        mock_commit = mock.Mock()
        mock_commit.created_at.date.return_value.isoformat.return_value = "2025-01-10"

        mock_pr = mock.Mock()
        mock_pr.created_at.date.return_value.isoformat.return_value = "2025-01-10"

        mock_issue = mock.Mock()
        mock_issue.created_at.date.return_value.isoformat.return_value = "2025-01-10"

        result = command.generate_heatmap_data([mock_commit], [mock_pr], [mock_issue])

        assert result == {"2025-01-10": 3}
