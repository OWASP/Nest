"""Tests for mentorship export utilities."""

import json
from datetime import date, datetime
from unittest.mock import MagicMock

import pytest

from apps.mentorship.utils.export import (
    MAX_EXPORT_LIMIT,
    ExportFormat,
    generate_export_filename,
    serialize_issues_to_csv,
    serialize_issues_to_json,
)


class MockLabel:
    """Mock label for testing."""

    def __init__(self, name: str):
        self.name = name


class MockUser:
    """Mock user for testing."""

    def __init__(self, login: str):
        self.login = login


class MockRepository:
    """Mock repository for testing."""

    def __init__(self, name: str):
        self.name = name


class MockIssue:
    """Mock issue for testing export serialization."""

    def __init__(
        self,
        number: int,
        title: str,
        state: str = "open",
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
        author_login: str = "testuser",
        created_at: datetime | None = None,
        url: str = "",
        repository_name: str = "test-repo",
    ):
        self.number = number
        self.title = title
        self.state = state
        self.url = url
        self.created_at = created_at or datetime(2024, 1, 15, 10, 30, 0)

        # Mock labels
        self._labels = [MockLabel(name) for name in (labels or [])]

        # Mock assignees
        self._assignees = [MockUser(login) for login in (assignees or [])]

        # Mock author
        self.author = MockUser(author_login) if author_login else None

        # Mock repository
        self.repository = MockRepository(repository_name)

    @property
    def labels(self):
        """Return mock labels manager."""
        mock = MagicMock()
        mock.all.return_value = self._labels
        return mock

    @property
    def assignees(self):
        """Return mock assignees manager."""
        mock = MagicMock()
        mock.all.return_value = self._assignees
        return mock


class TestSerializeIssuesToCsv:
    """Tests for CSV serialization."""

    def test_empty_list(self):
        """Should return CSV with headers only for empty list."""
        result = serialize_issues_to_csv([])

        # Should have BOM and headers
        assert result.startswith("\ufeff")
        assert "Number" in result
        assert "Title" in result
        assert "State" in result

    def test_single_issue(self):
        """Should serialize a single issue correctly."""
        issues = [
            MockIssue(
                number=123,
                title="Test Issue",
                state="open",
                labels=["bug"],
                assignees=["user1"],
            )
        ]

        result = serialize_issues_to_csv(issues)

        assert "123" in result
        assert "Test Issue" in result
        assert "open" in result
        assert "bug" in result
        assert "user1" in result

    def test_special_characters_escaped(self):
        """Should properly escape special characters in CSV."""
        issues = [
            MockIssue(
                number=1,
                title='Issue with "quotes" and, commas',
                state="open",
            )
        ]

        result = serialize_issues_to_csv(issues)

        # Title with special chars should be quoted
        assert '"Issue with ""quotes"" and, commas"' in result

    def test_multiple_labels_joined(self):
        """Should join multiple labels with semicolons."""
        issues = [
            MockIssue(
                number=1,
                title="Test",
                labels=["bug", "feature", "help wanted"],
            )
        ]

        result = serialize_issues_to_csv(issues)

        assert "bug; feature; help wanted" in result

    def test_newline_in_title(self):
        """Should handle newlines in title."""
        issues = [
            MockIssue(
                number=1,
                title="Line1\nLine2",
            )
        ]

        result = serialize_issues_to_csv(issues)

        # CSV should quote the field with newline
        assert '"Line1\nLine2"' in result


class TestSerializeIssuesToJson:
    """Tests for JSON serialization."""

    def test_empty_list(self):
        """Should return valid JSON with empty issues array."""
        result = serialize_issues_to_json([], module_key="test-module")
        data = json.loads(result)

        assert data["count"] == 0
        assert data["issues"] == []
        assert data["moduleKey"] == "test-module"
        assert "exportedAt" in data

    def test_single_issue(self):
        """Should serialize a single issue correctly."""
        issues = [
            MockIssue(
                number=456,
                title="JSON Test",
                state="closed",
                labels=["enhancement"],
                assignees=["contributor"],
                author_login="author1",
            )
        ]

        result = serialize_issues_to_json(issues, module_key="my-module")
        data = json.loads(result)

        assert data["count"] == 1
        assert len(data["issues"]) == 1

        issue = data["issues"][0]
        assert issue["number"] == 456
        assert issue["title"] == "JSON Test"
        assert issue["state"] == "closed"
        assert issue["labels"] == ["enhancement"]
        assert issue["assignees"] == ["contributor"]
        assert issue["author"] == "author1"

    def test_preserves_arrays(self):
        """Should preserve arrays for labels and assignees."""
        issues = [
            MockIssue(
                number=1,
                title="Test",
                labels=["a", "b", "c"],
                assignees=["x", "y"],
            )
        ]

        result = serialize_issues_to_json(issues)
        data = json.loads(result)

        assert isinstance(data["issues"][0]["labels"], list)
        assert isinstance(data["issues"][0]["assignees"], list)
        assert len(data["issues"][0]["labels"]) == 3
        assert len(data["issues"][0]["assignees"]) == 2


class TestGenerateExportFilename:
    """Tests for filename generation."""

    def test_csv_filename(self):
        """Should generate CSV filename with date."""
        result = generate_export_filename("test-module", ExportFormat.CSV)

        today = date.today().strftime("%Y-%m-%d")
        assert result == f"nest-test-module-issues-{today}.csv"

    def test_json_filename(self):
        """Should generate JSON filename with date."""
        result = generate_export_filename("my-project", ExportFormat.JSON)

        today = date.today().strftime("%Y-%m-%d")
        assert result == f"nest-my-project-issues-{today}.json"


class TestExportLimits:
    """Tests for export limits."""

    def test_max_export_limit_defined(self):
        """Should have a defined maximum export limit."""
        assert MAX_EXPORT_LIMIT == 1000
        assert MAX_EXPORT_LIMIT > 0
