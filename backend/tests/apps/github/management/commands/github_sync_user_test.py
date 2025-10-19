import io
from datetime import UTC, datetime

import pytest

from apps.github.management.commands.github_sync_user import Command


class TestGithubSyncUserCommand:
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
