"""Tests for OWASP Board of Directors sync command."""

import yaml
from unittest import mock

import pytest
import requests

from django.contrib.contenttypes.models import ContentType

from apps.github.models.user import User
from apps.owasp.management.commands.owasp_sync_board_members import Command
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.entity_member import EntityMember


class TestOwaspSyncBoardMembersCommand:
    """Test cases for OWASP Board of Directors sync command."""

    BOARD_HISTORY_URL = "https://raw.githubusercontent.com/OWASP/www-board/master/_data/board-history.yml"

    @pytest.fixture
    def command(self):
        """Return Command instance."""
        return Command()

    @pytest.fixture
    def mock_board_data(self):
        """Return mock board history data."""
        return [
            {
                "year": 2023,
                "members": [
                    {"name": "John Doe"},
                    {"name": "Jane Smith"},
                    {"name": "Bob Johnson"},
                ],
            },
            {
                "year": 2024,
                "members": [
                    {"name": "Alice Brown"},
                    {"name": "Charlie Davis"},
                ],
            },
        ]

    @pytest.fixture
    def mock_github_user(self):
        """Return mock GitHub user."""
        user = mock.Mock(spec=User)
        user.name = "John Doe"
        user.id = 1
        user.login = "johndoe"
        return user

    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.requests.get")
    @mock.patch("apps.owasp.models.board_of_directors.BoardOfDirectors.objects.get_or_create")
    @mock.patch("apps.owasp.models.entity_member.EntityMember.update_data")
    @mock.patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model")
    @mock.patch("django.db.transaction.atomic")
    def test_handle_successful_sync(
        self,
        mock_atomic,
        mock_get_content_type,
        mock_update_data,
        mock_get_or_create,
        mock_requests_get,
        command,
        mock_board_data,
    ):
        """Test successful board members sync for a specific year."""
        mock_response = mock.Mock()
        mock_response.text = yaml.dump(mock_board_data)
        mock_response.raise_for_status = mock.Mock()
        mock_requests_get.return_value = mock_response

        mock_board = mock.Mock(spec=BoardOfDirectors)
        mock_board.id = 1
        mock_get_or_create.return_value = (mock_board, False)

        mock_content_type = mock.Mock(spec=ContentType)
        mock_get_content_type.return_value = mock_content_type

        mock_entity_members = []
        for i in range(3):
            mock_entity_member = mock.Mock(spec=EntityMember)
            mock_entity_member.is_active = False  
            mock_entity_member.member_id = None   
            mock_entity_member.save = mock.Mock() 
            mock_entity_members.append(mock_entity_member)
        
        mock_update_data.side_effect = mock_entity_members

        mock_atomic.return_value.__enter__ = mock.Mock()
        mock_atomic.return_value.__exit__ = mock.Mock(return_value=None)

        command.handle(year=2023)

        mock_requests_get.assert_called_once_with(self.BOARD_HISTORY_URL, timeout=15)
        mock_get_or_create.assert_called_once_with(year=2023)
        mock_get_content_type.assert_called_once_with(BoardOfDirectors)
        
        assert mock_update_data.call_count == 3

        expected_calls = [
            mock.call(
                {
                    "entity_id": 1,
                    "entity_type": mock_content_type,
                    "member_name": "John Doe",
                    "role": EntityMember.Role.MEMBER,
                },
                save=True,
            ),
            mock.call(
                {
                    "entity_id": 1,
                    "entity_type": mock_content_type,
                    "member_name": "Jane Smith",
                    "role": EntityMember.Role.MEMBER,
                },
                save=True,
            ),
            mock.call(
                {
                    "entity_id": 1,
                    "entity_type": mock_content_type,
                    "member_name": "Bob Johnson",
                    "role": EntityMember.Role.MEMBER,
                },
                save=True,
            ),
        ]
        mock_update_data.assert_has_calls(expected_calls, any_order=True)
        
        for mock_entity_member in mock_entity_members:
            mock_entity_member.save.assert_called_once()
            call_args = mock_entity_member.save.call_args
            args, kwargs = call_args
            assert 'update_fields' in kwargs
            assert 'is_active' in kwargs['update_fields']

    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.requests.get")
    def test_handle_requests_exception(self, mock_requests_get, command):
        """Test handling of requests exception."""
        mock_requests_get.side_effect = requests.RequestException("Connection error")

        with mock.patch.object(command.stderr, "write") as mock_stderr:
            command.handle(year=2023)
            mock_stderr.assert_called_once()
            error_message = mock_stderr.call_args[0][0]
            assert "Failed to fetch or parse board history" in error_message

    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.requests.get")
    def test_handle_yaml_parse_error(self, mock_requests_get, command):
        """Test handling of YAML parse error."""
        mock_response = mock.Mock()
        mock_response.text = "invalid: yaml: content: ["
        mock_response.raise_for_status = mock.Mock()
        mock_requests_get.return_value = mock_response

        with mock.patch.object(command.stderr, "write") as mock_stderr:
            command.handle(year=2023)
            mock_stderr.assert_called_once()
            error_message = mock_stderr.call_args[0][0]
            assert "Failed to fetch or parse board history" in error_message

    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.requests.get")
    def test_handle_no_members_for_year(
        self, mock_requests_get, command, mock_board_data
    ):
        """Test handling when no board members found for specified year."""
        mock_response = mock.Mock()
        mock_response.text = yaml.dump(mock_board_data)
        mock_response.raise_for_status = mock.Mock()
        mock_requests_get.return_value = mock_response

        with mock.patch.object(command.stderr, "write") as mock_stderr:
            command.handle(year=2025)  # Year not in mock data
            mock_stderr.assert_called_once()
            error_message = mock_stderr.call_args[0][0]
            assert "No board members found for year 2025" in error_message

    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.requests.get")
    @mock.patch("apps.owasp.models.board_of_directors.BoardOfDirectors.objects.get_or_create")
    @mock.patch("apps.owasp.models.entity_member.EntityMember.update_data")
    @mock.patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model")
    @mock.patch("django.db.transaction.atomic")
    def test_handle_creates_new_board(
        self,
        mock_atomic,
        mock_get_content_type,
        mock_update_data,
        mock_get_or_create,
        mock_requests_get,
        command,
        mock_board_data,
    ):
        """Test that new BoardOfDirectors is created when needed."""
        mock_response = mock.Mock()
        mock_response.text = yaml.dump(mock_board_data)
        mock_response.raise_for_status = mock.Mock()
        mock_requests_get.return_value = mock_response

        mock_board = mock.Mock(spec=BoardOfDirectors)
        mock_board.id = 1
        mock_get_or_create.return_value = (mock_board, True)

        mock_content_type = mock.Mock(spec=ContentType)
        mock_get_content_type.return_value = mock_content_type

        mock_entity_member = mock.Mock(spec=EntityMember)
        mock_update_data.return_value = mock_entity_member

        mock_atomic.return_value.__enter__ = mock.Mock()
        mock_atomic.return_value.__exit__ = mock.Mock(return_value=None)

        with mock.patch.object(command.stdout, "write") as mock_stdout:
            command.handle(year=2023)
            stdout_calls = [str(call) for call in mock_stdout.call_args_list]
            created_message_found = any("Created new BoardOfDirectors for year 2023" in call for call in stdout_calls)
            assert created_message_found

        mock_get_or_create.assert_called_once_with(year=2023)

    def test_extract_board_members_for_year(self, command, mock_board_data):
        """Test extraction of board members for specific year."""
        members = command._extract_board_members_for_year(mock_board_data, 2023)

        assert len(members) == 3
        assert members[0]["name"] == "John Doe"
        assert members[1]["name"] == "Jane Smith"
        assert members[2]["name"] == "Bob Johnson"

    def test_extract_board_members_for_nonexistent_year(self, command, mock_board_data):
        """Test extraction for year that doesn't exist."""
        members = command._extract_board_members_for_year(mock_board_data, 2025)

        assert members == []

    @mock.patch("apps.owasp.models.entity_member.EntityMember.update_data")
    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.Command._fuzzy_match_github_user")
    def test_create_or_update_member_with_github_match(
        self, mock_fuzzy_match, mock_update_data, command, mock_github_user
    ):
        """Test creating member with GitHub user match."""
        mock_board = mock.Mock(spec=BoardOfDirectors)
        mock_board.id = 1
        mock_content_type = mock.Mock(spec=ContentType)

        mock_fuzzy_match.return_value = mock_github_user
        mock_update_data.return_value = mock.Mock(spec=EntityMember)

        member_data = {"name": "John Doe"}

        command._create_or_update_member(member_data, mock_board, mock_content_type)

        mock_fuzzy_match.assert_called_once_with("John Doe")
        mock_update_data.assert_called_once()

        call_args = mock_update_data.call_args
        assert call_args[0][0]["member"] == mock_github_user
        assert call_args[0][0]["member_name"] == "John Doe"

    @mock.patch("apps.owasp.models.entity_member.EntityMember.update_data")
    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.Command._fuzzy_match_github_user")
    def test_create_or_update_member_without_github_match(
        self, mock_fuzzy_match, mock_update_data, command
    ):
        """Test creating member without GitHub user match."""
        mock_board = mock.Mock(spec=BoardOfDirectors)
        mock_board.id = 1
        mock_content_type = mock.Mock(spec=ContentType)

        mock_fuzzy_match.return_value = None
        mock_update_data.return_value = mock.Mock(spec=EntityMember)

        member_data = {"name": "John Doe"}

        command._create_or_update_member(member_data, mock_board, mock_content_type)

        mock_fuzzy_match.assert_called_once_with("John Doe")
        mock_update_data.assert_called_once()

        call_args = mock_update_data.call_args
        assert "member" not in call_args[0][0]

    @mock.patch("apps.owasp.models.entity_member.EntityMember.update_data")
    def test_create_or_update_member_with_empty_name(self, mock_update_data, command):
        """Test that member with empty name is skipped."""
        mock_board = mock.Mock(spec=BoardOfDirectors)
        mock_content_type = mock.Mock(spec=ContentType)

        command._create_or_update_member({"name": ""}, mock_board, mock_content_type)
        mock_update_data.assert_not_called()

        command._create_or_update_member({"name": "  "}, mock_board, mock_content_type)
        mock_update_data.assert_not_called()

    @mock.patch("apps.owasp.models.entity_member.EntityMember.update_data")
    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.Command._fuzzy_match_github_user")
    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.logger")
    def test_create_or_update_member_update_exception(
        self, mock_logger, mock_fuzzy_match, mock_update_data, command
    ):
        """Test handling of exception during member update."""
        mock_board = mock.Mock(spec=BoardOfDirectors)
        mock_board.id = 1
        mock_content_type = mock.Mock(spec=ContentType)

        mock_fuzzy_match.return_value = None
        mock_update_data.side_effect = Exception("Database error")

        member_data = {"name": "John Doe"}

        command._create_or_update_member(member_data, mock_board, mock_content_type)

        mock_update_data.assert_called_once()
        mock_logger.error.assert_called_once_with(
            "Failed to process board member %s: %s", "John Doe", "Database error"
        )

    @mock.patch("apps.github.models.user.User.objects.filter")
    def test_fuzzy_match_github_user_exact_match(self, mock_filter, command, mock_github_user):
        """Test fuzzy matching with exact name match."""
        mock_queryset = mock.Mock()
        mock_queryset.first.return_value = mock_github_user
        mock_filter.return_value = mock_queryset

        result = command._fuzzy_match_github_user("John Doe")

        assert result == mock_github_user
        mock_filter.assert_called_with(name__iexact="John Doe")

    @mock.patch("apps.github.models.user.User.objects.filter")
    def test_fuzzy_match_github_user_no_match(self, mock_filter, command):
        """Test fuzzy matching with no match found."""
        mock_exact_queryset = mock.Mock()
        mock_exact_queryset.first.return_value = None

        mock_candidate_queryset = mock.Mock()
        mock_candidate_queryset.count.return_value = 0
        mock_candidate_queryset.exclude.return_value = mock_candidate_queryset

        mock_filter.side_effect = [mock_exact_queryset, mock_candidate_queryset]

        result = command._fuzzy_match_github_user("Unknown Person")

        assert result is None

    def test_fuzzy_match_github_user_empty_name(self, command):
        """Test fuzzy matching with empty name."""
        result = command._fuzzy_match_github_user("")
        assert result is None

        result = command._fuzzy_match_github_user(None)
        assert result is None

    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.fuzz")
    @mock.patch("apps.github.models.user.User.objects.filter")
    def test_fuzzy_match_github_user_with_similarity(self, mock_filter, mock_fuzz, command):
        """Test fuzzy matching using similarity threshold."""
        mock_exact_queryset = mock.Mock()
        mock_exact_queryset.first.return_value = None

        user1 = mock.Mock(spec=User)
        user1.name = "Jon Doe"  
        user2 = mock.Mock(spec=User) 
        user2.name = "John Doe Jr"  

        mock_candidate_queryset = mock.Mock()
        mock_candidate_queryset.count.return_value = 2
        mock_candidate_queryset.exclude.return_value = mock_candidate_queryset
        mock_candidate_queryset.__iter__ = mock.Mock(return_value=iter([user1, user2]))

        mock_filter.side_effect = [mock_exact_queryset, mock_candidate_queryset]

        mock_fuzz.ratio.side_effect = [75, 85] 

        result = command._fuzzy_match_github_user("John Doe")

        assert result == user2
        assert mock_fuzz.ratio.call_count == 2

    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.logger")
    @mock.patch("apps.github.models.user.User.objects.filter")
    def test_fuzzy_match_github_user_exception(self, mock_filter, mock_logger, command):
        """Test fuzzy matching handles exceptions gracefully."""
        mock_filter.side_effect = Exception("Database error")

        result = command._fuzzy_match_github_user("John Doe")

        assert result is None
        mock_logger.warning.assert_called_once_with(
            "Failed to match GitHub user for %s: %s", "John Doe", mock.ANY
        )

    @pytest.mark.parametrize("year", [2020, 2023, 2024])
    def test_add_arguments(self, command, year):
        """Test command arguments parsing."""
        parser = mock.Mock()
        command.add_arguments(parser)

        parser.add_argument.assert_called_once_with(
            "--year",
            type=int,
            help="Specific year to sync board members for",
            required=True,
        )

    @mock.patch("apps.owasp.management.commands.owasp_sync_board_members.requests.get")
    @mock.patch("apps.owasp.models.board_of_directors.BoardOfDirectors.objects.get_or_create")
    @mock.patch("apps.owasp.models.entity_member.EntityMember.update_data")
    @mock.patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model")
    @mock.patch("django.db.transaction.atomic")
    def test_progress_reporting(
        self,
        mock_atomic,
        mock_get_content_type,
        mock_update_data,
        mock_get_or_create,
        mock_requests_get,
        command,
    ):
        """Test progress reporting during sync."""
        board_data = [
            {
                "year": 2023,
                "members": [{"name": f"Member {i}"} for i in range(15)],
            }
        ]

        mock_response = mock.Mock()
        mock_response.text = yaml.dump(board_data)
        mock_response.raise_for_status = mock.Mock()
        mock_requests_get.return_value = mock_response

        mock_board = mock.Mock(spec=BoardOfDirectors)
        mock_board.id = 1
        mock_get_or_create.return_value = (mock_board, True)

        mock_content_type = mock.Mock(spec=ContentType)
        mock_get_content_type.return_value = mock_content_type

        mock_entity_member = mock.Mock(spec=EntityMember)
        mock_update_data.return_value = mock_entity_member

        mock_atomic.return_value.__enter__ = mock.Mock()
        mock_atomic.return_value.__exit__ = mock.Mock(return_value=None)

        with mock.patch.object(command.stdout, "write") as mock_stdout:
            command.handle(year=2023)

            stdout_calls = [str(call) for call in mock_stdout.call_args_list]
            progress_message_found = any("Processed 10 of 15 members" in call for call in stdout_calls)
            assert progress_message_found