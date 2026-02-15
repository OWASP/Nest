from unittest.mock import MagicMock, patch

import pytest
import strawberry

from apps.github.models import User as GithubUser
from apps.mentorship.api.internal.nodes.program import PaginatedPrograms
from apps.mentorship.api.internal.queries.program import ProgramQuery
from apps.mentorship.models import Program


@pytest.fixture
def api_program_queries() -> ProgramQuery:
    """Pytest fixture to return an instance of the query resolver class."""
    return ProgramQuery()


@pytest.fixture
def mock_info() -> MagicMock:
    """Fixture for a mock strawberry.Info object."""
    mock_github_user = MagicMock(spec=GithubUser, id=1, login="testuser")
    mock_user = MagicMock(id=1)
    mock_user.github_user = mock_github_user
    mock_request = MagicMock()
    mock_request.user = mock_user
    mock_info = MagicMock(spec=strawberry.Info)
    mock_info.context.request = mock_request
    return mock_info


class TestGetProgram:
    """Tests for the get_program query."""

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_get_program_success(
        self, mock_program_prefetch_related: MagicMock, mock_info: MagicMock, api_program_queries
    ) -> None:
        """Test successful retrieval of a program by key."""
        mock_program = MagicMock(spec=Program)
        mock_program_prefetch_related.return_value.get.return_value = mock_program

        result = api_program_queries.get_program(program_key="program1")

        assert result == mock_program
        mock_program_prefetch_related.assert_called_once_with(
            "admins__github_user", "admins__nest_user"
        )
        mock_program_prefetch_related.return_value.get.assert_called_once_with(key="program1")

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_get_program_does_not_exist(
        self, mock_program_prefetch_related: MagicMock, mock_info: MagicMock, api_program_queries
    ) -> None:
        """Test when the program does not exist."""
        mock_program_prefetch_related.return_value.get.side_effect = Program.DoesNotExist

        result = api_program_queries.get_program(program_key="nonexistent")

        assert result is None
        mock_program_prefetch_related.assert_called_once_with(
            "admins__github_user", "admins__nest_user"
        )
        mock_program_prefetch_related.return_value.get.assert_called_once_with(key="nonexistent")


class TestMyPrograms:
    """Tests for the my_programs query."""

    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_success(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test successful retrieval of user's programs as admin and mentor."""
        mock_program_admin_filter.return_value.values_list.return_value = [1, 2]

        mock_admin = MagicMock(nest_user_id=1)
        mock_mentor_admin = MagicMock(nest_user_id=999)  # Different user for mentor check

        mock_admin_program = MagicMock(spec=Program, nest_created_at="2023-01-01", id=1)
        mock_admin_program.admins.all.return_value = [mock_admin]
        mock_admin_program.modules.return_value.mentors.return_value.github_user.return_value = []

        mock_mentor_program = MagicMock(spec=Program, nest_created_at="2023-01-02", id=2)
        mock_mentor_program.admins.all.return_value = []
        mock_mentor_program.modules.return_value.mentors.return_value = [mock_mentor_admin]

        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 2
        mock_queryset.order_by.return_value.__getitem__.return_value = [
            mock_mentor_program,
            mock_admin_program,
        ]
        mock_queryset.filter.return_value = mock_queryset

        mock_program_prefetch.return_value.filter.return_value.distinct.return_value = (
            mock_queryset
        )

        result = api_program_queries.my_programs(info=mock_info)

        assert isinstance(result, PaginatedPrograms)
        assert len(result.programs) == 2
        assert result.total_pages == 1
        assert result.current_page == 1
        assert result.programs[0].user_role == "mentor"
        assert result.programs[1].user_role == "admin"

        mock_program_admin_filter.assert_called_once()
        mock_program_prefetch.assert_called_once_with(
            "admins__github_user",
            "admins__nest_user",
            "modules__mentors__github_user",
        )
        mock_program_prefetch.return_value.filter.assert_called_once()
        mock_queryset.order_by.assert_called_once_with("-nest_created_at")

    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_no_admin_programs(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test when the current user is not an admin of any program."""
        mock_program_admin_filter.return_value.values_list.return_value = []

        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_queryset.order_by.return_value.__getitem__.return_value = []
        mock_queryset.filter.return_value = mock_queryset

        mock_program_prefetch.return_value.filter.return_value.distinct.return_value = (
            mock_queryset
        )

        result = api_program_queries.my_programs(info=mock_info)

        assert isinstance(result, PaginatedPrograms)
        assert result.programs == []
        assert result.total_pages == 1
        assert result.current_page == 1

    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_no_programs_found(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test when no programs are found for the user."""
        mock_program_admin_filter.return_value.values_list.return_value = [1, 2]

        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_queryset.order_by.return_value.__getitem__.return_value = []
        mock_queryset.filter.return_value = mock_queryset

        mock_program_prefetch.return_value.filter.return_value.distinct.return_value = (
            mock_queryset
        )

        result = api_program_queries.my_programs(info=mock_info)

        assert isinstance(result, PaginatedPrograms)
        assert result.programs == []
        assert result.total_pages == 1
        assert result.current_page == 1

    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_with_search(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test my_programs with a search query."""
        mock_program_admin_filter.return_value.values_list.return_value = [1]

        mock_admin = MagicMock(nest_user_id=1)
        mock_program = MagicMock(spec=Program, nest_created_at="2023-01-01", id=1)
        mock_program.admins.all.return_value = [mock_admin]
        mock_program.modules.return_value.mentors.return_value.github_user.return_value = []

        mock_queryset_filtered = MagicMock()
        mock_queryset_filtered.count.return_value = 1
        mock_queryset_filtered.order_by.return_value.__getitem__.return_value = [mock_program]

        mock_queryset_initial = MagicMock()
        mock_queryset_initial.filter.return_value.distinct.return_value.filter.return_value = (
            mock_queryset_filtered
        )
        mock_program_prefetch.return_value = mock_queryset_initial

        result = api_program_queries.my_programs(info=mock_info, search="test")

        assert len(result.programs) == 1
        mock_program_prefetch_filter = mock_program_prefetch.return_value.filter.return_value
        mock_program_prefetch_filter.distinct.return_value.filter.assert_called_once_with(
            name__icontains="test"
        )

    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_pagination(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test pagination for my_programs query."""
        mock_program_admin_filter.return_value.values_list.return_value = [1, 2, 3]

        mock_admin = MagicMock(nest_user_id=1)
        mock_program1 = MagicMock(spec=Program, nest_created_at="2023-01-03", id=1)
        mock_program1.admins.all.return_value = [mock_admin]
        mock_program1.modules.return_value.mentors.return_value.github_user.return_value = []

        mock_program2 = MagicMock(spec=Program, nest_created_at="2023-01-02", id=2)
        mock_program2.admins.all.return_value = []
        mock_program2.modules.return_value.mentors.return_value = [mock_admin]

        mock_program3 = MagicMock(spec=Program, nest_created_at="2023-01-01", id=3)
        mock_program3.admins.all.return_value = [mock_admin]
        mock_program3.modules.return_value.mentors.return_value.github_user.return_value = []

        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 3
        mock_queryset.order_by.return_value.__getitem__.return_value = [mock_program2]
        mock_queryset.filter.return_value = mock_queryset

        mock_program_prefetch.return_value.filter.return_value.distinct.return_value = (
            mock_queryset
        )

        result = api_program_queries.my_programs(info=mock_info, page=2, limit=1)

        assert len(result.programs) == 1
        assert result.programs[0].id == 2
        assert result.total_pages == 3
        assert result.current_page == 2
