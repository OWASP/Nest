from unittest.mock import MagicMock, patch

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
    """Tests for Program.user_has_access, which delegates to get_user_role."""

    def test_no_role_has_no_access(self):
        """A user with no role in the program (get_user_role -> None) has no access."""
        program = MagicMock(spec=Program)
        program.get_user_role.return_value = None

        assert Program.user_has_access(program, MagicMock()) is False

    def test_admin_has_access(self):
        """A program admin has access."""
        program = MagicMock(spec=Program)
        program.get_user_role.return_value = "admin"

        assert Program.user_has_access(program, MagicMock()) is True

    def test_mentor_has_access(self):
        """A mentor of the program has access."""
        program = MagicMock(spec=Program)
        program.get_user_role.return_value = "mentor"

        assert Program.user_has_access(program, MagicMock()) is True

    def test_mentee_has_access(self):
        """A mentee enrolled in the program has access."""
        program = MagicMock(spec=Program)
        program.get_user_role.return_value = "mentee"

        assert Program.user_has_access(program, MagicMock()) is True


class TestProgramGetUserRole:
    """Tests for Program.get_user_role, including its authentication gate."""

    def test_anonymous_user_has_no_role(self):
        """Unauthenticated users get no role and never trigger a role lookup."""
        mock_user = MagicMock()
        mock_user.is_authenticated = False

        program = MagicMock(spec=Program)

        assert Program.get_user_role(program, mock_user) is None
        program.has_admin.assert_not_called()
        program.modules.filter.assert_not_called()

    def test_admin_returns_admin(self):
        """An admin resolves to the admin role and short-circuits other lookups."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True

        program = MagicMock(spec=Program)
        program.has_admin.return_value = True

        assert Program.get_user_role(program, mock_user) == "admin"
        program.modules.filter.assert_not_called()

    def test_mentor_returns_mentor(self):
        """A non-admin who mentors a module resolves to the mentor role."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = MagicMock()

        program = MagicMock(spec=Program)
        program.has_admin.return_value = False
        program.modules.filter.return_value.exists.return_value = True

        assert Program.get_user_role(program, mock_user) == "mentor"

    def test_mentee_returns_mentee(self):
        """A non-admin non-mentor enrolled as a mentee resolves to the mentee role."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = MagicMock()

        program = MagicMock(spec=Program)
        program.has_admin.return_value = False
        program.modules.filter.return_value.exists.side_effect = [False, True]

        assert Program.get_user_role(program, mock_user) == "mentee"

    def test_authenticated_user_without_role_returns_none(self):
        """An authenticated user with no admin/mentor/mentee tie gets no role."""
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.github_user = MagicMock()

        program = MagicMock(spec=Program)
        program.has_admin.return_value = False
        program.modules.filter.return_value.exists.side_effect = [False, False]

        assert Program.get_user_role(program, mock_user) is None


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
