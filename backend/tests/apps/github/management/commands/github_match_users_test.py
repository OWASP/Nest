"""Tests for the github_match_users Django management command."""

from unittest.mock import MagicMock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.github.management.commands.github_match_users import Command


@pytest.fixture
def command():
    """Return a command instance with a mocked stdout."""
    cmd = Command()
    cmd.stdout = MagicMock()
    return cmd


class TestGithubMatchUsersCommand:
    """Test suite for the command's setup and helper methods."""

    def test_command_help_text(self, command):
        """Test that the command has the new, correct help text."""
        assert (
            command.help
            == "Matches entity leader names with GitHub Users and creates EntityMember records."
        )

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_add_arguments(self, command):
        """Test that the command adds the correct arguments for the new version."""
        parser = MagicMock()
        command.add_arguments(parser)

        assert parser.add_argument.call_count == 2
        parser.add_argument.assert_any_call(
            "model_name",
            type=str,
            choices=("chapter", "committee", "project", "all"),
            help="Model to process: chapter, committee, project, or all.",
        )
        parser.add_argument.assert_any_call(
            "--threshold",
            type=int,
            default=75,
            help="Threshold for fuzzy matching (0-100)",
        )

    @pytest.mark.parametrize(
        ("login", "name", "expected"),
        [
            ("validlogin", "Valid Name", True),
            ("ok", "Valid Name", True),
            ("validlogin", "V", False),
            ("v", "Valid Name", False),
            ("v", "V", False),
            ("", "", False),
            ("validlogin", "", False),
            ("", "Valid Name", False),
            ("validlogin", None, False),
        ],
    )
    def test_is_valid_user(self, command, login, name, expected):
        """Test the _is_valid_user method."""
        with patch("apps.github.management.commands.github_match_users.ID_MIN_LENGTH", 2):
            assert command._is_valid_user(login, name) == expected


class TestFindUserMatches:
    """Test suite for the _find_user_matches helper method."""

    @pytest.fixture
    def mock_users(self):
        """Return a dictionary of mock users."""
        return [
            {"id": 1, "login": "john_doe", "name": "John Doe"},
            {"id": 2, "login": "jane_doe", "name": "Jane Doe"},
            {"id": 3, "login": "peter_jones", "name": "Peter Jones"},
        ]

    def test_exact_match(self, command, mock_users):
        """Test exact matching by login and name."""
        leaders_raw = ["john_doe", "Jane Doe"]
        matches = command._find_user_matches(leaders_raw, mock_users, 90)

        assert len(matches) == 2
        assert any(u["id"] == 1 for u in matches)
        assert any(u["id"] == 2 for u in matches)

    @patch("apps.github.management.commands.github_match_users.fuzz")
    def test_fuzzy_match(self, mock_fuzz, command, mock_users):
        """Test fuzzy matching."""
        mock_fuzz.token_sort_ratio.side_effect = lambda _, s2: 90 if "peter" in s2.lower() else 10
        leaders_raw = ["pete_jones"]
        matches = command._find_user_matches(leaders_raw, mock_users, 80)

        assert len(matches) == 1
        assert matches[0]["id"] == 3

    def test_unmatched_leader(self, command, mock_users):
        """Test that an unknown leader returns no matches."""
        leaders_raw = ["unknown_leader"]
        matches = command._find_user_matches(leaders_raw, mock_users, 100)
        assert matches == []
