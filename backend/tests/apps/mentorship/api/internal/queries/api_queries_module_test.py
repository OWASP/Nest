from unittest.mock import MagicMock, patch

import pytest
import strawberry

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

    @patch("apps.mentorship.api.internal.queries.module.has_program_access")
    @patch("apps.mentorship.api.internal.queries.module.Program.objects.get")
    def test_get_program_modules_hidden_for_draft_program(
        self,
        mock_program_get: MagicMock,
        mock_has_access: MagicMock,
        mock_anonymous_info: MagicMock,
        api_module_queries,
    ) -> None:
        """Test that modules of a draft program are hidden from anonymous users."""
        mock_program = MagicMock(spec=Program)
        mock_program.status = Program.ProgramStatus.DRAFT
        mock_program_get.return_value = mock_program
        mock_has_access.return_value = False

        result = api_module_queries.get_program_modules(
            info=mock_anonymous_info, program_key="draft-program"
        )

        assert result == []

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.filter")
    def test_get_project_modules_success(
        self, mock_module_filter: MagicMock, api_module_queries
    ) -> None:
        """Test successful retrieval of modules by project key."""
        mock_module = MagicMock(spec=Module)
        mock_module_filter_related = mock_module_filter.return_value.select_related.return_value
        mock_module_filter_related.prefetch_related.return_value.order_by.return_value = [
            mock_module
        ]

        result = api_module_queries.get_project_modules(project_key="project1")

        assert result == [mock_module]
        mock_module_filter.assert_called_once_with(
            project__key="project1",
            program__status=Program.ProgramStatus.PUBLISHED,
        )

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.filter")
    def test_get_project_modules_empty(
        self, mock_module_filter: MagicMock, api_module_queries
    ) -> None:
        """Test retrieval of modules by project key returns empty list if no modules found."""
        mock_module_filter_related = mock_module_filter.return_value.select_related.return_value
        mock_module_filter_related.prefetch_related.return_value.order_by.return_value = []

        result = api_module_queries.get_project_modules(project_key="nonexistent_project")

        assert result == []
        mock_module_filter.assert_called_once_with(
            project__key="nonexistent_project",
            program__status=Program.ProgramStatus.PUBLISHED,
        )

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

    @patch("apps.mentorship.api.internal.queries.module.has_program_access")
    @patch("apps.mentorship.api.internal.queries.module.Module.objects.select_related")
    def test_get_module_hidden_for_draft_program(
        self,
        mock_module_select_related: MagicMock,
        mock_has_access: MagicMock,
        mock_anonymous_info: MagicMock,
        api_module_queries,
    ) -> None:
        """Test that a module of a draft program is hidden from anonymous users."""
        mock_program = MagicMock(spec=Program)
        mock_program.status = Program.ProgramStatus.DRAFT
        mock_module = MagicMock(spec=Module)
        mock_module.program = mock_program
        mock_module_select_related.return_value.prefetch_related.return_value.get.return_value = (
            mock_module
        )
        mock_has_access.return_value = False

        result = api_module_queries.get_module(
            info=mock_anonymous_info, module_key="module1", program_key="draft-program"
        )

        assert result is None
