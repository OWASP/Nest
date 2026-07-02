from unittest.mock import MagicMock, patch

import pytest
import strawberry
from graphql import GraphQLError

from apps.github.models import User as GithubUser
from apps.mentorship.api.internal.queries.module import ModuleQuery
from apps.mentorship.models import Module, Program


@pytest.fixture
def api_module_queries() -> ModuleQuery:
    """Pytest fixture to return an instance of the query resolver class."""
    return ModuleQuery()


@pytest.fixture
def mock_info() -> MagicMock:
    """Fixture for a mock strawberry.Info object with an authenticated user."""
    mock_github_user = MagicMock(spec=GithubUser, id=1, login="testuser")
    mock_user = MagicMock(id=1)
    mock_user.github_user = mock_github_user
    mock_user.is_authenticated = True
    mock_request = MagicMock()
    mock_request.user = mock_user
    mock_info = MagicMock(spec=strawberry.Info)
    mock_info.context.request = mock_request
    return mock_info


@pytest.fixture
def mock_anonymous_info() -> MagicMock:
    """Fixture for a mock strawberry.Info object with an anonymous user."""
    mock_user = MagicMock(id=None)
    mock_user.is_authenticated = False
    mock_user.github_user = None
    mock_request = MagicMock()
    mock_request.user = mock_user
    mock_info = MagicMock(spec=strawberry.Info)
    mock_info.context.request = mock_request
    return mock_info


class TestModuleQuery:
    """Tests for ModuleQuery."""

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.filter")
    @patch("apps.mentorship.api.internal.queries.module.Program.objects.get")
    def test_get_program_modules_success(
        self,
        mock_program_get: MagicMock,
        mock_module_filter: MagicMock,
        mock_info: MagicMock,
        api_module_queries,
    ) -> None:
        """Test successful retrieval of modules by program key."""
        mock_program = MagicMock(spec=Program)
        mock_program.status = Program.ProgramStatus.PUBLISHED
        mock_program_get.return_value = mock_program

        mock_module = MagicMock(spec=Module)
        mock_module_filter_related = mock_module_filter.return_value.select_related.return_value
        mock_module_filter_related.prefetch_related.return_value.order_by.return_value = [
            mock_module
        ]
        result = api_module_queries.get_program_modules(info=mock_info, program_key="program1")

        assert result == [mock_module]
        mock_program_get.assert_called_once_with(key="program1")
        mock_module_filter.assert_called_once_with(program=mock_program)

    @patch("apps.mentorship.api.internal.queries.module.Program.objects.get")
    def test_get_program_modules_empty(
        self,
        mock_program_get: MagicMock,
        mock_info: MagicMock,
        api_module_queries,
    ) -> None:
        """Test retrieval of modules returns empty list if program not found."""
        mock_program_get.side_effect = Program.DoesNotExist

        result = api_module_queries.get_program_modules(
            info=mock_info, program_key="nonexistent_program"
        )

        assert result == []
        mock_program_get.assert_called_once_with(key="nonexistent_program")

    @patch("apps.mentorship.api.internal.queries.module.Program.objects.get")
    def test_get_program_modules_hidden_for_draft_program(
        self,
        mock_program_get: MagicMock,
        mock_anonymous_info: MagicMock,
        api_module_queries,
    ) -> None:
        """Test that modules of a draft program are hidden from anonymous users."""
        mock_program = MagicMock(spec=Program)
        mock_program.status = Program.ProgramStatus.DRAFT
        mock_program_get.return_value = mock_program
        mock_program.user_has_access.return_value = False

        result = api_module_queries.get_program_modules(
            info=mock_anonymous_info, program_key="draft-program"
        )

        assert result == []

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.select_related")
    def test_get_module_success(
        self, mock_module_select_related: MagicMock, mock_info: MagicMock, api_module_queries
    ) -> None:
        """Test successful retrieval of a single module."""
        mock_program = MagicMock(spec=Program)
        mock_program.status = Program.ProgramStatus.PUBLISHED
        mock_module = MagicMock(spec=Module)
        mock_module.program = mock_program
        mock_module_select_related.return_value.prefetch_related.return_value.get.return_value = (
            mock_module
        )

        result = api_module_queries.get_module(
            info=mock_info, module_key="module1", program_key="program1"
        )

        assert result == mock_module
        mock_module_select_related.assert_called_once_with("program", "project")
        mock_module_select_related.return_value.prefetch_related.return_value.get.assert_called_once_with(
            key="module1", program__key="program1"
        )

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.select_related")
    def test_get_module_does_not_exist(
        self, mock_module_select_related: MagicMock, mock_info: MagicMock, api_module_queries
    ) -> None:
        """Test when the module does not exist."""
        mock_module_select_related.return_value.prefetch_related.return_value.get.side_effect = (
            Module.DoesNotExist
        )

        result = api_module_queries.get_module(
            info=mock_info, module_key="nonexistent", program_key="program1"
        )
        assert result is None
        mock_module_select_related.assert_called_once_with("program", "project")
        mock_module_select_related.return_value.prefetch_related.return_value.get.assert_called_once_with(
            key="nonexistent", program__key="program1"
        )

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.select_related")
    def test_get_module_hidden_for_draft_program(
        self,
        mock_module_select_related: MagicMock,
        mock_anonymous_info: MagicMock,
        api_module_queries,
    ) -> None:
        """Test that a module of a draft program is hidden from anonymous users."""
        mock_program = MagicMock(spec=Program)
        mock_program.status = Program.ProgramStatus.DRAFT
        mock_program.user_has_access.return_value = False
        mock_module = MagicMock(spec=Module)
        mock_module.program = mock_program
        mock_module_select_related.return_value.prefetch_related.return_value.get.return_value = (
            mock_module
        )

        result = api_module_queries.get_module(
            info=mock_anonymous_info, module_key="module1", program_key="draft-program"
        )

        assert result is None

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.filter")
    @patch("apps.mentorship.api.internal.queries.module.Program.objects.get")
    def test_management_program_modules_admin_sees_all(
        self,
        mock_program_get: MagicMock,
        mock_module_filter: MagicMock,
        mock_info: MagicMock,
        api_module_queries,
    ) -> None:
        """Program admins receive every module without mentor filtering."""
        mock_program = MagicMock(spec=Program)
        mock_program.user_has_access.return_value = True
        mock_program.has_admin.return_value = True
        mock_program_get.return_value = mock_program

        mock_module = MagicMock(spec=Module)
        mock_chain = mock_module_filter.return_value.select_related.return_value
        mock_chain.prefetch_related.return_value.distinct.return_value.order_by.return_value = [
            mock_module
        ]

        result = api_module_queries.get_management_program_modules(
            info=mock_info, program_key="program1"
        )

        assert result == [mock_module]
        mock_module_filter.assert_called_once_with(program=mock_program)
        # No per-mentor filtering applied for admins.
        mock_module_filter.return_value.filter.assert_not_called()

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.filter")
    @patch("apps.mentorship.api.internal.queries.module.Program.objects.get")
    def test_management_program_modules_mentor_sees_only_assigned(
        self,
        mock_program_get: MagicMock,
        mock_module_filter: MagicMock,
        mock_info: MagicMock,
        api_module_queries,
    ) -> None:
        """Mentors receive only modules they are assigned to."""
        mock_program = MagicMock(spec=Program)
        mock_program.user_has_access.return_value = True
        mock_program.has_admin.return_value = False
        mock_program_get.return_value = mock_program

        mock_module = MagicMock(spec=Module)
        mock_chain = (
            mock_module_filter.return_value.filter.return_value.select_related.return_value
        )
        mock_chain.prefetch_related.return_value.distinct.return_value.order_by.return_value = [
            mock_module
        ]

        result = api_module_queries.get_management_program_modules(
            info=mock_info, program_key="program1"
        )

        assert result == [mock_module]
        mock_module_filter.assert_called_once_with(program=mock_program)
        # Mentor filtering is applied (filter called again with a Q on the queryset).
        mock_module_filter.return_value.filter.assert_called_once()

    @patch("apps.mentorship.api.internal.queries.module.Program.objects.get")
    def test_management_program_modules_forbidden(
        self,
        mock_program_get: MagicMock,
        mock_info: MagicMock,
        api_module_queries,
    ) -> None:
        """Non-staff users cannot list modules via management query."""
        mock_program = MagicMock(spec=Program)
        mock_program.user_has_access.return_value = False
        mock_program_get.return_value = mock_program

        with pytest.raises(GraphQLError) as exc_info:
            api_module_queries.get_management_program_modules(
                info=mock_info, program_key="program1"
            )

        assert exc_info.value.extensions["code"] == "FORBIDDEN"

    def test_management_program_modules_unauthenticated(
        self, mock_anonymous_info: MagicMock, api_module_queries
    ) -> None:
        """Anonymous users cannot call get_management_program_modules."""
        with pytest.raises(GraphQLError) as exc_info:
            api_module_queries.get_management_program_modules(
                info=mock_anonymous_info, program_key="program1"
            )

        assert exc_info.value.extensions["code"] == "UNAUTHORIZED"

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.select_related")
    def test_management_module_admin_success(
        self, mock_module_select_related: MagicMock, mock_info: MagicMock, api_module_queries
    ) -> None:
        """Program admins receive any module via get_management_module."""
        mock_program = MagicMock(spec=Program)
        mock_program.has_admin.return_value = True
        mock_module = MagicMock(spec=Module)
        mock_module.program = mock_program
        mock_module_select_related.return_value.prefetch_related.return_value.get.return_value = (
            mock_module
        )

        result = api_module_queries.get_management_module(
            info=mock_info, module_key="module1", program_key="program1"
        )

        assert result == mock_module

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.select_related")
    def test_management_module_assigned_mentor_success(
        self,
        mock_module_select_related: MagicMock,
        mock_info: MagicMock,
        api_module_queries,
    ) -> None:
        """A mentor assigned to the module receives it via get_management_module."""
        mock_program = MagicMock(spec=Program)
        mock_program.has_admin.return_value = False
        mock_module = MagicMock(spec=Module)
        mock_module.program = mock_program
        mock_module.has_mentor.return_value = True
        mock_module_select_related.return_value.prefetch_related.return_value.get.return_value = (
            mock_module
        )

        result = api_module_queries.get_management_module(
            info=mock_info, module_key="module1", program_key="program1"
        )

        assert result == mock_module

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.select_related")
    def test_management_module_unassigned_mentor_forbidden(
        self,
        mock_module_select_related: MagicMock,
        mock_info: MagicMock,
        api_module_queries,
    ) -> None:
        """A user who is neither admin, mentor, nor mentee of this module is forbidden."""
        mock_program = MagicMock(spec=Program)
        mock_program.has_admin.return_value = False
        mock_module = MagicMock(spec=Module)
        mock_module.program = mock_program
        mock_module.has_mentor.return_value = False
        mock_module.has_mentee.return_value = False
        mock_module_select_related.return_value.prefetch_related.return_value.get.return_value = (
            mock_module
        )

        with pytest.raises(GraphQLError) as exc_info:
            api_module_queries.get_management_module(
                info=mock_info, module_key="module1", program_key="program1"
            )

        assert exc_info.value.extensions["code"] == "FORBIDDEN"

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.select_related")
    def test_management_module_not_found(
        self, mock_module_select_related: MagicMock, mock_info: MagicMock, api_module_queries
    ) -> None:
        """Missing module returns None for get_management_module."""
        mock_module_select_related.return_value.prefetch_related.return_value.get.side_effect = (
            Module.DoesNotExist
        )

        result = api_module_queries.get_management_module(
            info=mock_info, module_key="nonexistent", program_key="program1"
        )

        assert result is None
        mock_module_select_related.assert_called_once_with("program", "project")
        mock_module_select_related.return_value.prefetch_related.return_value.get.assert_called_once_with(
            key="nonexistent", program__key="program1"
        )

    def test_management_module_unauthenticated(
        self, mock_anonymous_info: MagicMock, api_module_queries
    ) -> None:
        """Anonymous users cannot call get_management_module."""
        with pytest.raises(GraphQLError) as exc_info:
            api_module_queries.get_management_module(
                info=mock_anonymous_info, module_key="module1", program_key="program1"
            )

        assert exc_info.value.extensions["code"] == "UNAUTHORIZED"
