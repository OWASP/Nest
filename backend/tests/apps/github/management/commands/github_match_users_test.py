"""Tests for the github_match_users Django management command."""

from unittest.mock import MagicMock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.github.management.commands.github_match_users import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


class TestGithubMatchUsersCommand:
    """Test suite for the github_match_users command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert (
            command.help
            == "Match leaders or Slack members with GitHub users using exact and fuzzy matching."
        )

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_add_arguments(self, command):
        """Test that the command adds the correct arguments."""
        parser = MagicMock()
        command.add_arguments(parser)
        assert parser.add_argument.call_count == 2
        parser.add_argument.assert_any_call(
            "model_name",
            type=str,
            choices=("chapter", "committee", "member", "project"),
            help="Model name to process: chapter, committee, project, or member",
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


class TestProcessLeaders:
    """Test suite for the process_leaders method."""

    @pytest.fixture
    def command(self):
        """Return a command instance."""
        command = Command()
        command.stdout = MagicMock()
        return command

    @pytest.fixture
    def mock_users(self):
        """Return a dictionary of mock users."""
        return {
            1: {"id": 1, "login": "john_doe", "name": "John Doe"},
            2: {"id": 2, "login": "jane_doe", "name": "Jane Doe"},
            3: {"id": 3, "login": "peter_jones", "name": "Peter Jones"},
            4: {"id": 4, "login": "testuser", "name": "Test User"},
        }

    def test_no_leaders(self, command):
        """Test with no leaders provided."""
        exact, fuzzy, unmatched = command.process_leaders([], 75, {})
        assert exact == []
        assert fuzzy == []
        assert unmatched == []

    def test_exact_match(self, command, mock_users):
        """Test exact matching."""
        leaders_raw = ["john_doe", "Jane Doe"]
        exact, fuzzy, unmatched = command.process_leaders(leaders_raw, 75, mock_users)
        assert len(exact) == 2
        assert mock_users[1] in exact
        assert mock_users[2] in exact
        assert fuzzy == []
        assert unmatched == []

    @patch("apps.github.management.commands.github_match_users.fuzz")
    def test_fuzzy_match(self, mock_fuzz, command, mock_users):
        """Test fuzzy matching."""
        mock_fuzz.token_sort_ratio.side_effect = lambda left, right: (
            90 if "peter" in right.lower() or "peter" in left.lower() else 10
        )

        leaders_raw = ["pete_jones"]
        exact, fuzzy, unmatched = command.process_leaders(leaders_raw, 80, mock_users)
        assert exact == []
        assert len(fuzzy) == 1
        assert mock_users[3] in fuzzy
        assert unmatched == []

    def test_unmatched_leader(self, command, mock_users):
        """Test unmatched leader."""
        leaders_raw = ["unknown_leader"]
        exact, fuzzy, unmatched = command.process_leaders(leaders_raw, 100, mock_users)
        assert exact == []
        assert fuzzy == []
        assert unmatched == ["unknown_leader"]

    def test_mixed_matches(self, command, mock_users):
        """Test a mix of exact, fuzzy, and unmatched leaders."""
        leaders_raw = ["john_doe", "pete_jones", "unknown_leader"]
        with patch("apps.github.management.commands.github_match_users.fuzz") as mock_fuzz:

            def ratio(s1, s2):
                return 85 if "peter" in s2.lower() and "pete" in s1.lower() else 50

            mock_fuzz.token_sort_ratio.side_effect = ratio
            exact, fuzzy, unmatched = command.process_leaders(leaders_raw, 80, mock_users)
        assert len(exact) == 1
        assert mock_users[1] in exact
        assert len(fuzzy) == 1
        assert mock_users[3] in fuzzy
        assert unmatched == ["unknown_leader"]

    def test_duplicate_leaders(self, command, mock_users):
        """Test with duplicate leaders in raw list."""
        leaders_raw = ["john_doe", "john_doe"]
        exact, fuzzy, unmatched = command.process_leaders(leaders_raw, 75, mock_users)
        assert len(exact) == 1
        assert mock_users[1] in exact
        assert fuzzy == []
        assert unmatched == []

    def test_empty_and_none_leaders(self, command, mock_users):
        """Test with empty string and None in leaders raw list."""
        leaders_raw = ["", None, "john_doe"]
        exact, fuzzy, unmatched = command.process_leaders(leaders_raw, 75, mock_users)
        assert len(exact) == 1
        assert mock_users[1] in exact
        assert fuzzy == []
        assert unmatched == []

    def test_multiple_exact_matches_for_one_leader(self, command):
        """Test when one leader name matches multiple users."""
        users = {
            1: {"id": 1, "login": "johndoe", "name": "Johnathan Doe"},
            2: {"id": 2, "login": "JohnDoe", "name": "John Doe"},
        }
        leaders_raw = ["JohnDoe"]
        exact, fuzzy, unmatched = command.process_leaders(leaders_raw, 75, users)
        assert len(exact) == 2
        assert users[1] in exact
        assert users[2] in exact
        assert fuzzy == []
        assert unmatched == []


@patch("apps.github.management.commands.github_match_users.User")
@patch("apps.github.management.commands.github_match_users.Chapter")
@patch("apps.github.management.commands.github_match_users.Committee")
@patch("apps.github.management.commands.github_match_users.Project")
@patch("apps.github.management.commands.github_match_users.Member")
class TestHandleMethod:
    """Test suite for the handle method of the command."""

    @pytest.fixture
    def command(self):
        """Return a command instance with mocked stdout."""
        command = Command()
        command.stdout = MagicMock()
        return command

    def test_invalid_model_name(
        self,
        mock_member,
        mock_project,
        mock_committee,
        mock_chapter,
        mock_user,
        command,
    ):
        """Test handle with an invalid model name."""
        command.handle(model_name="invalid", threshold=75)
        command.stdout.write.assert_called_with(
            command.style.ERROR(
                "Invalid model name! Choose from: chapter, committee, project, member"
            )
        )

    @pytest.mark.parametrize(
        ("model_name", "model_class_str", "relation_field"),
        [
            ("chapter", "Chapter", "suggested_leaders"),
            ("committee", "Committee", "suggested_leaders"),
            ("project", "Project", "suggested_leaders"),
            ("member", "Member", "suggested_users"),
        ],
    )
    def test_handle_with_valid_models(
        self,
        mock_member,
        mock_project,
        mock_committee,
        mock_chapter,
        mock_user,
        command,
        model_name,
        model_class_str,
        relation_field,
    ):
        """Test handle with different valid models."""
        mock_models = {
            "Chapter": mock_chapter,
            "Committee": mock_committee,
            "Project": mock_project,
            "Member": mock_member,
        }
        model_class = mock_models[model_class_str]
        mock_user.objects.values.return_value = [
            {"id": 1, "login": "leader_one", "name": "Leader One"},
            {"id": 2, "login": "leader_two", "name": "Leader Two"},
        ]
        mock_instance = MagicMock()
        mock_instance.id = 1
        if model_name == "member":
            mock_instance.username = "leader_one"
            mock_instance.real_name = "Leader Two"
        else:
            mock_instance.leaders_raw = ["leader_one", "leader_two"]
        model_class.objects.prefetch_related.return_value = [mock_instance]
        command.handle(model_name=model_name, threshold=90)
        model_class.objects.prefetch_related.assert_called_once_with(relation_field)
        relation = getattr(mock_instance, relation_field)
        relation.set.assert_called_once_with({1, 2})
        command.stdout.write.assert_any_call(f"Processing {model_name} 1...")
        command.stdout.write.assert_any_call("Exact match found for leader_one: leader_one")

    def test_handle_with_no_users(
        self,
        mock_member,
        mock_project,
        mock_committee,
        mock_chapter,
        mock_user,
        command,
    ):
        """Test handle when there are no users in the database."""
        mock_user.objects.values.return_value = []
        mock_chapter_instance = MagicMock(id=1, leaders_raw=["some_leader"])
        mock_chapter.objects.prefetch_related.return_value = [mock_chapter_instance]
        command.handle(model_name="chapter", threshold=75)
        command.stdout.write.assert_any_call("Processing chapter 1...")
        unmatched_call = [
            c for c in command.stdout.write.call_args_list if "Unmatched" in c.args[0]
        ]
        assert len(unmatched_call) == 1
        assert "['some_leader']" in unmatched_call[0].args[0]
        mock_chapter_instance.suggested_leaders.set.assert_called_once_with(set())

    def test_handle_with_no_leaders_in_instance(
        self,
        mock_member,
        mock_project,
        mock_committee,
        mock_chapter,
        mock_user,
        command,
    ):
        """Test handle when an instance has no leaders."""
        mock_user.objects.values.return_value = [
            {"id": 1, "login": "user1", "name": "User One"},
        ]
        mock_chapter_instance = MagicMock(id=1, leaders_raw=[])
        mock_chapter.objects.prefetch_related.return_value = [mock_chapter_instance]
        command.handle(model_name="chapter", threshold=75)
        command.stdout.write.assert_any_call("Processing chapter 1...")
        unmatched_call = [
            c for c in command.stdout.write.call_args_list if "Unmatched" in c.args[0]
        ]
        assert len(unmatched_call) == 0
        mock_chapter_instance.suggested_leaders.set.assert_called_once_with(set())
