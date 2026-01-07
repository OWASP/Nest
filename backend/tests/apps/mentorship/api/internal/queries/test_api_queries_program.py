"""Pytest for mentorship program queries."""

from unittest.mock import MagicMock, patch

import pytest
import strawberry
from django.core.exceptions import ObjectDoesNotExist

from apps.github.models import User as GithubUser
from apps.mentorship.api.internal.nodes.program import PaginatedPrograms
from apps.mentorship.api.internal.queries.program import ProgramQuery
from apps.mentorship.models import Mentor, Program


class TestGetProgram:
    """Tests for the get_program query."""

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_get_program_success(self, mock_program_prefetch_related: MagicMock) -> None:
        """Test successful retrieval of a program by key."""
        mock_program = MagicMock(spec=Program)
        mock_program_prefetch_related.return_value.get.return_value = mock_program

        query = ProgramQuery()
        result = query.get_program(program_key="program1")

        assert result == mock_program
        mock_program_prefetch_related.assert_called_once_with("admins__github_user")
        mock_program_prefetch_related.return_value.get.assert_called_once_with(key="program1")

    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_get_program_does_not_exist(self, mock_program_prefetch_related: MagicMock) -> None:
        """Test when the program does not exist."""
        mock_program_prefetch_related.return_value.get.side_effect = Program.DoesNotExist

        query = ProgramQuery()
        with pytest.raises(ObjectDoesNotExist, match="Program with key 'nonexistent' not found."):
            query.get_program(program_key="nonexistent")

        mock_program_prefetch_related.assert_called_once_with("admins__github_user")
        mock_program_prefetch_related.return_value.get.assert_called_once_with(key="nonexistent")


class TestMyPrograms:
    """Tests for the my_programs query."""

    @pytest.fixture
    def mock_info(self) -> MagicMock:
        """Fixture for a mock strawberry.Info object."""
        mock_github_user = MagicMock(spec=GithubUser, id=1, login="testuser")
        mock_user = MagicMock()
        mock_user.github_user = mock_github_user
        mock_request = MagicMock()
        mock_request.user = mock_user
        mock_info = MagicMock(spec=strawberry.Info)
        mock_info.context.request = mock_request
        return mock_info

    @patch("apps.mentorship.api.internal.queries.program.Mentor.objects.select_related")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_success(
        self, mock_program_prefetch: MagicMock, mock_mentor_select: MagicMock, mock_info: MagicMock
    ) -> None:
        """Test successful retrieval of user's programs as admin and mentor."""
        mock_mentor = MagicMock(spec=Mentor, id=1)
        mock_mentor_select.return_value.get.return_value = mock_mentor

        mock_admin_program = MagicMock(spec=Program, nest_created_at="2023-01-01", id=1)
        mock_admin_program.admins.all.return_value = [mock_mentor]
        mock_admin_program.modules.return_value.mentors.return_value.github_user.return_value = []

        mock_mentor_program = MagicMock(spec=Program, nest_created_at="2023-01-02", id=2)
        mock_mentor_program.admins.all.return_value = []
        mock_mentor_program.modules.return_value.mentors.return_value = [mock_mentor]

        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 2
        mock_queryset.order_by.return_value.__getitem__.return_value = [
            mock_mentor_program,
            mock_admin_program,
        ]
        mock_queryset.filter.return_value = mock_queryset  # For search chain

        mock_program_prefetch.return_value.filter.return_value.distinct.return_value = (
            mock_queryset
        )

        query = ProgramQuery()
        result = query.my_programs(info=mock_info)

        assert isinstance(result, PaginatedPrograms)
        assert len(result.programs) == 2
        assert result.total_pages == 1
        assert result.current_page == 1
        assert result.programs[0].user_role == "mentor"
        assert result.programs[1].user_role == "admin"

        mock_mentor_select.return_value.get.assert_called_once()
        mock_program_prefetch.assert_called_once_with(
            "admins__github_user", "modules__mentors__github_user"
        )
        mock_program_prefetch.return_value.filter.assert_called_once()
        mock_queryset.order_by.assert_called_once_with("-nest_created_at")

    @patch("apps.mentorship.api.internal.queries.program.Mentor.objects.select_related")
    def test_my_programs_mentor_does_not_exist(
        self, mock_mentor_select: MagicMock, mock_info: MagicMock
    ) -> None:
        """Test when the current user is not a mentor."""
        mock_mentor_select.return_value.get.side_effect = Mentor.DoesNotExist

        query = ProgramQuery()
        result = query.my_programs(info=mock_info)

        assert isinstance(result, PaginatedPrograms)
        assert result.programs == []
        assert result.total_pages == 0
        assert result.current_page == 1
        mock_mentor_select.return_value.get.assert_called_once()

    @patch("apps.mentorship.api.internal.queries.program.Mentor.objects.select_related")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_no_programs_found(
        self, mock_program_prefetch: MagicMock, mock_mentor_select: MagicMock, mock_info: MagicMock
    ) -> None:
        """Test when no programs are found for the mentor."""
        mock_mentor = MagicMock(spec=Mentor, id=1)
        mock_mentor_select.return_value.get.return_value = mock_mentor

        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_queryset.order_by.return_value.__getitem__.return_value = []
        mock_queryset.filter.return_value = mock_queryset

        mock_program_prefetch.return_value.filter.return_value.distinct.return_value = (
            mock_queryset
        )

        query = ProgramQuery()
        result = query.my_programs(info=mock_info)

        assert isinstance(result, PaginatedPrograms)
        assert result.programs == []
        assert result.total_pages == 1
        assert result.current_page == 1

    @patch("apps.mentorship.api.internal.queries.program.Mentor.objects.select_related")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_with_search(
        self, mock_program_prefetch: MagicMock, mock_mentor_select: MagicMock, mock_info: MagicMock
    ) -> None:
        """Test my_programs with a search query."""
        mock_mentor = MagicMock(spec=Mentor, id=1)
        mock_mentor_select.return_value.get.return_value = mock_mentor

        mock_program = MagicMock(spec=Program, nest_created_at="2023-01-01", id=1)
        mock_program.admins.all.return_value = [mock_mentor]
        mock_program.modules.return_value.mentors.return_value.github_user.return_value = []

        mock_queryset_filtered = MagicMock()
        mock_queryset_filtered.count.return_value = 1
        mock_queryset_filtered.order_by.return_value.__getitem__.return_value = [mock_program]

        mock_queryset_initial = MagicMock()
        mock_queryset_initial.filter.return_value.distinct.return_value.filter.return_value = (
            mock_queryset_filtered
        )
        mock_program_prefetch.return_value = mock_queryset_initial

        query = ProgramQuery()
        result = query.my_programs(info=mock_info, search="test")

        assert len(result.programs) == 1
        mock_program_prefetch.return_value.filter.return_value.distinct.return_value.filter.assert_called_once_with(
            name__icontains="test"
        )

    @patch("apps.mentorship.api.internal.queries.program.Mentor.objects.select_related")
    @patch("apps.mentorship.api.internal.queries.program.Program.objects.prefetch_related")
    def test_my_programs_pagination(
        self, mock_program_prefetch: MagicMock, mock_mentor_select: MagicMock, mock_info: MagicMock
    ) -> None:
        """Test pagination for my_programs query."""
        mock_mentor = MagicMock(spec=Mentor, id=1)
        mock_mentor_select.return_value.get.return_value = mock_mentor

        mock_program1 = MagicMock(spec=Program, nest_created_at="2023-01-03", id=1)
        mock_program1.admins.all.return_value = [mock_mentor]
        mock_program1.modules.return_value.mentors.return_value.github_user.return_value = []

        mock_program2 = MagicMock(spec=Program, nest_created_at="2023-01-02", id=2)
        mock_program2.admins.all.return_value = []
        mock_program2.modules.return_value.mentors.return_value = [mock_mentor]

        mock_program3 = MagicMock(spec=Program, nest_created_at="2023-01-01", id=3)
        mock_program3.admins.all.return_value = [mock_mentor]
        mock_program3.modules.return_value.mentors.return_value.github_user.return_value = []

        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 3
        mock_queryset.order_by.return_value.__getitem__.return_value = [mock_program2]
        mock_queryset.filter.return_value = mock_queryset

        mock_program_prefetch.return_value.filter.return_value.distinct.return_value = (
            mock_queryset
        )

        query = ProgramQuery()
        result = query.my_programs(info=mock_info, page=2, limit=1)

        assert len(result.programs) == 1
        assert result.programs[0].id == 2
        assert result.total_pages == 3
        assert result.current_page == 2
