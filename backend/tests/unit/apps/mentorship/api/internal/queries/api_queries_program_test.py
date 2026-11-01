from unittest.mock import MagicMock, patch

import pytest
import strawberry
from graphql import GraphQLError

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


class TestGetProgram:
    """Tests for the get_program query."""

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_get_program_success(
        self, mock_program_prefetch_related: MagicMock, mock_info: MagicMock, api_program_queries
    ) -> None:
        """Test successful retrieval of a published program by key."""
        mock_program = MagicMock(spec=Program)
        mock_program.status = Program.ProgramStatus.PUBLISHED
        mock_program_prefetch_related.return_value.get.return_value = mock_program

        result = api_program_queries.get_program(info=mock_info, program_key="program1")

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

        result = api_program_queries.get_program(info=mock_info, program_key="nonexistent")

        assert result is None
        mock_program_prefetch_related.assert_called_once_with(
            "admins__github_user", "admins__nest_user"
        )
        mock_program_prefetch_related.return_value.get.assert_called_once_with(key="nonexistent")

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_get_draft_program_hidden_for_anonymous_user(
        self,
        mock_program_prefetch_related: MagicMock,
        mock_anonymous_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test that a draft program is not visible to anonymous users."""
        mock_program = MagicMock(spec=Program)
        mock_program.status = Program.ProgramStatus.DRAFT
        mock_program_prefetch_related.return_value.get.return_value = mock_program
        mock_program.user_has_access.return_value = False

        result = api_program_queries.get_program(
            info=mock_anonymous_info, program_key="draft-program"
        )

        assert result is None

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_get_draft_program_visible_for_admin(
        self,
        mock_program_prefetch_related: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test that a draft program is visible to an admin."""
        mock_program = MagicMock(spec=Program)
        mock_program.status = Program.ProgramStatus.DRAFT
        mock_program_prefetch_related.return_value.get.return_value = mock_program
        mock_program.user_has_access.return_value = True

        result = api_program_queries.get_program(info=mock_info, program_key="draft-program")

        assert result == mock_program


class TestManagementProgram:
    """Tests for the get_management_program query (staff-only management UI)."""

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_management_program_success(
        self, mock_program_prefetch_related: MagicMock, mock_info: MagicMock, api_program_queries
    ) -> None:
        """A user with a role receives the program, with user_role populated."""
        mock_program = MagicMock(spec=Program)
        mock_program.status = Program.ProgramStatus.PUBLISHED
        mock_program_prefetch_related.return_value.get.return_value = mock_program
        mock_program.get_user_role.return_value = "mentor"

        result = api_program_queries.get_management_program(info=mock_info, program_key="program1")

        assert result == mock_program
        assert mock_program.user_role == "mentor"
        mock_program.get_user_role.assert_called_once_with(mock_info.context.request.user)

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_management_program_forbidden_when_no_role(
        self,
        mock_program_prefetch_related: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """A user with no role in the program is forbidden from the management view."""
        mock_program = MagicMock(spec=Program)
        mock_program.status = Program.ProgramStatus.PUBLISHED
        mock_program_prefetch_related.return_value.get.return_value = mock_program
        mock_program.get_user_role.return_value = None

        with pytest.raises(GraphQLError) as exc_info:
            api_program_queries.get_management_program(info=mock_info, program_key="program1")

        assert exc_info.value.extensions["code"] == "FORBIDDEN"

    def test_management_program_unauthenticated(
        self, mock_anonymous_info: MagicMock, api_program_queries
    ) -> None:
        """Anonymous users cannot call get_management_program."""
        with pytest.raises(GraphQLError) as exc_info:
            api_program_queries.get_management_program(
                info=mock_anonymous_info, program_key="program1"
            )

        assert exc_info.value.extensions["code"] == "UNAUTHORIZED"

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_management_program_not_found(
        self, mock_program_prefetch_related: MagicMock, mock_info: MagicMock, api_program_queries
    ) -> None:
        """Missing program returns None."""
        mock_program_prefetch_related.return_value.get.side_effect = Program.DoesNotExist

        result = api_program_queries.get_management_program(info=mock_info, program_key="missing")

        assert result is None


def _wire_role_lookups(
    mock_program_admin_filter: MagicMock,
    mock_program_objects_filter: MagicMock,
    *,
    admin_program_ids=(),
    admin_ids=(),
    mentor_ids=(),
    mentee_ids=(),
) -> None:
    """Wire the bulk per-page role lookups used by my_programs.

    ProgramAdmin.objects.filter(...).values_list is called twice: first for the
    admin program ids used in the OR filter, then for the page-scoped admin ids.
    Program.objects.filter(...).values_list is called for mentor ids, then mentee ids.
    """
    mock_program_admin_filter.return_value.values_list.side_effect = [
        list(admin_program_ids),
        list(admin_ids),
    ]
    mentor_qs = MagicMock()
    mentor_qs.values_list.return_value = list(mentor_ids)
    mentee_qs = MagicMock()
    mentee_qs.values_list.return_value = list(mentee_ids)
    mock_program_objects_filter.side_effect = [mentor_qs, mentee_qs]


class TestMyPrograms:
    """Tests for the my_programs query."""

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_success(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_program_objects_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test successful retrieval of user's programs as admin and mentor."""
        _wire_role_lookups(
            mock_program_admin_filter,
            mock_program_objects_filter,
            admin_program_ids=[1, 2],
            admin_ids=[1],
            mentor_ids=[2],
        )

        mock_admin_program = MagicMock(spec=Program, nest_created_at="2023-01-01", id=1)
        mock_mentor_program = MagicMock(spec=Program, nest_created_at="2023-01-02", id=2)

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

        mock_program_prefetch.assert_called_once_with(
            "admins__github_user",
            "admins__nest_user",
            "modules__mentors__github_user",
            "modules__mentors__nest_user",
        )
        mock_program_prefetch.return_value.filter.assert_called_once()
        mock_queryset.order_by.assert_called_once_with("-nest_created_at")

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_includes_mentee_role(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_program_objects_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """A program the user is only enrolled in as a mentee is labeled 'mentee'."""
        _wire_role_lookups(
            mock_program_admin_filter,
            mock_program_objects_filter,
            admin_program_ids=[],
            admin_ids=[],
            mentor_ids=[],
            mentee_ids=[5],
        )

        mock_mentee_program = MagicMock(spec=Program, nest_created_at="2023-01-01", id=5)

        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.order_by.return_value.__getitem__.return_value = [mock_mentee_program]
        mock_queryset.filter.return_value = mock_queryset
        mock_program_prefetch.return_value.filter.return_value.distinct.return_value = (
            mock_queryset
        )

        result = api_program_queries.my_programs(info=mock_info)

        assert len(result.programs) == 1
        assert result.programs[0].user_role == "mentee"

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_no_admin_programs(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_program_objects_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test when the current user is not an admin of any program."""
        _wire_role_lookups(mock_program_admin_filter, mock_program_objects_filter)

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

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_no_programs_found(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_program_objects_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test when no programs are found for the user."""
        _wire_role_lookups(
            mock_program_admin_filter, mock_program_objects_filter, admin_program_ids=[1, 2]
        )

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

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_with_search(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_program_objects_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test my_programs with a search query."""
        _wire_role_lookups(
            mock_program_admin_filter,
            mock_program_objects_filter,
            admin_program_ids=[1],
            admin_ids=[1],
        )

        mock_program = MagicMock(spec=Program, nest_created_at="2023-01-01", id=1)

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

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_pagination(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_program_objects_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test pagination for my_programs query."""
        _wire_role_lookups(
            mock_program_admin_filter,
            mock_program_objects_filter,
            admin_program_ids=[1, 2, 3],
            mentor_ids=[2],
        )

        mock_program2 = MagicMock(spec=Program, nest_created_at="2023-01-02", id=2)

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
        assert result.programs[0].user_role == "mentor"
        assert result.total_pages == 3
        assert result.current_page == 2

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_invalid_limit_uses_default(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_program_objects_filter: MagicMock,
        mock_info: MagicMock,
        api_program_queries,
    ) -> None:
        """Test that invalid limit (0) falls back to PAGE_SIZE default."""
        _wire_role_lookups(
            mock_program_admin_filter,
            mock_program_objects_filter,
            admin_program_ids=[1],
            admin_ids=[1],
        )

        mock_program = MagicMock(spec=Program, nest_created_at="2023-01-01", id=1)

        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 26
        mock_queryset.order_by.return_value.__getitem__.return_value = [mock_program]
        mock_queryset.filter.return_value = mock_queryset

        mock_program_prefetch.return_value.filter.return_value.distinct.return_value = (
            mock_queryset
        )

        result = api_program_queries.my_programs(info=mock_info, limit=0)

        assert isinstance(result, PaginatedPrograms)
        assert result.total_pages == 2

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.ProgramAdmin.objects.filter")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_no_github_user(
        self,
        mock_program_prefetch: MagicMock,
        mock_program_admin_filter: MagicMock,
        mock_program_objects_filter: MagicMock,
        api_program_queries,
    ) -> None:
        """Nest user without GitHub FK still sees admin programs; mentor OR uses nest_user too."""
        mock_user = MagicMock(id=1)
        mock_user.github_user = None
        mock_user.github_user_id = None
        mock_info_obj = MagicMock(spec=strawberry.Info)
        mock_info_obj.context.request.user = mock_user

        _wire_role_lookups(
            mock_program_admin_filter,
            mock_program_objects_filter,
            admin_program_ids=[1],
            admin_ids=[1],
        )

        mock_program = MagicMock(spec=Program, nest_created_at="2023-01-01", id=1)

        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.order_by.return_value.__getitem__.return_value = [mock_program]
        mock_queryset.filter.return_value = mock_queryset

        mock_program_prefetch.return_value.filter.return_value.distinct.return_value = (
            mock_queryset
        )

        result = api_program_queries.my_programs(info=mock_info_obj)

        assert isinstance(result, PaginatedPrograms)
        assert len(result.programs) == 1
        assert result.programs[0].user_role == "admin"
