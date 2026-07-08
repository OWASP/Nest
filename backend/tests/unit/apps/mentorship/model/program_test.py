from unittest.mock import MagicMock, patch

from apps.github.models import User as GithubUser
from apps.mentorship.models import Program


class TestProgram:
    def test_program_status_choices(self):
        assert Program.ProgramStatus.DRAFT == "draft"
        assert Program.ProgramStatus.PUBLISHED == "published"
        assert Program.ProgramStatus.COMPLETED == "completed"

    def test_str_returns_name(self):
        mock_program_instance = MagicMock(spec=Program)
        mock_program_instance.name = "Security Program"
        assert Program.__str__(mock_program_instance) == "Security Program"

    @patch("apps.common.models.TimestampedModel.save")
    def test_save_sets_key_from_name(self, mock_super_save):
        """Test save method sets key from slug name."""
        mock_program = MagicMock(spec=Program)
        mock_program.name = "My Test Program"

        Program.save(mock_program)

        assert mock_program.key == "my-test-program"
        mock_super_save.assert_called_once()


class TestProgramUserHasAccess:
    """Tests for Program.user_has_access method."""

    def test_anonymous_user_has_no_access(self):
        """Test that anonymous users do not have access."""
        mock_user = MagicMock()
        mock_user.is_authenticated = False

        program = MagicMock(spec=Program)

        assert Program.user_has_access(program, mock_user) is False

    def test_admin_has_access(self):
        """Test that a program admin has access."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = True

        assert Program.user_has_access(program, mock_user) is True

    def test_mentor_has_access(self):
        """Test that a mentor of the program has access."""
        mock_github_user = MagicMock(spec=GithubUser, id=1, login="testuser")
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = mock_github_user

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = False
        program.modules.filter.return_value.exists.return_value = True

        assert Program.user_has_access(program, mock_user) is True

    def test_authenticated_non_admin_non_mentor_has_no_access(self):
        """Test that an authenticated user who is not admin or mentor has no access."""
        mock_github_user = MagicMock(spec=GithubUser, id=1, login="testuser")
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = mock_github_user

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = False
        program.modules.filter.return_value.exists.return_value = False

        assert Program.user_has_access(program, mock_user) is False

    def test_authenticated_user_without_github_user(self):
        """User without github_user who is not admin or nest_user mentor has no access."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = None

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = False
        program.modules.filter.return_value.exists.return_value = False

        assert Program.user_has_access(program, mock_user) is False


class TestProgramHasAdmin:
    """Tests for Program.has_admin method."""

    def test_anonymous_user_is_not_admin(self):
        """Anonymous users are never admins."""
        mock_user = MagicMock()
        mock_user.is_authenticated = False

        program = MagicMock(spec=Program)

        assert Program.has_admin(program, mock_user) is False
        program.admins.filter.assert_not_called()

    def test_admin_match_returns_true(self):
        """A matching admin (via nest_user or github_user) makes the user an admin."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = MagicMock()

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = True

        assert Program.has_admin(program, mock_user) is True

    def test_github_user_fallback_included_in_query(self):
        """The lookup includes a github_user fallback clause when one is available."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = MagicMock()

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = True

        assert Program.has_admin(program, mock_user) is True
        # A single combined query is issued, including the github_user fallback.
        program.admins.filter.assert_called_once()
        query = program.admins.filter.call_args.args[0]
        assert ("nest_user", mock_user) in query.children
        assert ("github_user", mock_user.github_user) in query.children

    def test_authenticated_non_admin_is_not_admin(self):
        """An authenticated non-admin user is not an admin."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = MagicMock()

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = False

        assert Program.has_admin(program, mock_user) is False

    def test_user_without_github_user_omits_github_clause(self):
        """A user without a github_user is matched on nest_user only."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = None

        program = MagicMock(spec=Program)
        program.admins.filter.return_value.exists.return_value = False

        assert Program.has_admin(program, mock_user) is False
        query = program.admins.filter.call_args.args[0]
        assert ("nest_user", mock_user) in query.children
        assert all(child[0] != "github_user" for child in query.children)
