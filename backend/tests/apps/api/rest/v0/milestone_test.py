from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.milestone import MilestoneDetail, get_milestone, list_milestones
from apps.github.models.milestone import Milestone as MilestoneModel


class TestMilestoneSchema:
    @pytest.mark.parametrize(
        "milestone_data",
        [
            {
                "body": "This is a test milestone for Q1",
                "closed_issues_count": 5,
                "created_at": "2024-01-01T00:00:00Z",
                "due_on": "2024-03-31T23:59:59Z",
                "number": 1,
                "open_issues_count": 3,
                "state": "open",
                "title": "Q1 2024 Release",
                "updated_at": "2024-01-15T00:00:00Z",
                "url": "https://github.com/OWASP/Nest/milestone/1",
            },
            {
                "body": "Completed milestone for Q4 2023",
                "closed_issues_count": 15,
                "created_at": "2023-10-01T00:00:00Z",
                "due_on": "2023-12-31T23:59:59Z",
                "number": 2,
                "open_issues_count": 0,
                "state": "closed",
                "title": "Q4 2023 Release",
                "updated_at": "2024-01-05T00:00:00Z",
                "url": "https://github.com/OWASP/Nest/milestone/2",
            },
            {
                "body": "Milestone without due date",
                "closed_issues_count": 2,
                "created_at": "2024-02-01T00:00:00Z",
                "due_on": None,
                "number": 3,
                "open_issues_count": 8,
                "state": "open",
                "title": "Backlog",
                "updated_at": "2024-02-15T00:00:00Z",
                "url": "https://github.com/OWASP/Nest/milestone/3",
            },
        ],
    )
    def test_milestone_schema(self, milestone_data):
        milestone = MilestoneDetail(**milestone_data)

        assert milestone.body == milestone_data["body"]
        assert milestone.closed_issues_count == milestone_data["closed_issues_count"]
        assert milestone.created_at == datetime.fromisoformat(milestone_data["created_at"])
        if milestone_data["due_on"]:
            assert milestone.due_on == datetime.fromisoformat(milestone_data["due_on"])
        else:
            assert milestone.due_on is None
        assert milestone.number == milestone_data["number"]
        assert milestone.open_issues_count == milestone_data["open_issues_count"]
        assert milestone.state == milestone_data["state"]
        assert milestone.title == milestone_data["title"]
        assert milestone.updated_at == datetime.fromisoformat(milestone_data["updated_at"])
        assert milestone.url == milestone_data["url"]

    def test_milestone_schema_with_minimal_data(self):
        """Test milestone schema with minimal required fields."""
        minimal_data = {
            "body": "",
            "closed_issues_count": 0,
            "created_at": "2024-01-01T00:00:00Z",
            "due_on": None,
            "number": 1,
            "open_issues_count": 0,
            "state": "open",
            "title": "Test Milestone",
            "updated_at": "2024-01-01T00:00:00Z",
            "url": "https://github.com/test/repo/milestone/1",
        }
        milestone = MilestoneDetail(**minimal_data)

        assert milestone.body == ""
        assert milestone.closed_issues_count == 0
        assert milestone.due_on is None
        assert milestone.number == 1
        assert milestone.open_issues_count == 0
        assert milestone.title == "Test Milestone"
        assert milestone.state == "open"


class TestListMilestones:
    """Test cases for list_milestones endpoint."""

    @patch("apps.api.rest.v0.milestone.MilestoneModel.objects")
    def test_list_milestones_with_custom_ordering(self, mock_objects):
        """Test listing milestones with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = None
        mock_filters.state = None

        mock_select_related = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select_related
        mock_select_related.order_by.return_value = mock_ordered

        result = list_milestones(mock_request, filters=mock_filters, ordering="created_at")

        mock_objects.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select_related.order_by.assert_called_once_with("created_at", "id")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.milestone.MilestoneModel.objects")
    def test_list_milestones_ordering_by_updated_at(self, mock_objects):
        """Test listing milestones with ordering by updated_at avoids double ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = None
        mock_filters.state = None

        mock_select_related = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select_related
        mock_select_related.order_by.return_value = mock_ordered

        result = list_milestones(mock_request, filters=mock_filters, ordering="-updated_at")

        mock_objects.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select_related.order_by.assert_called_once_with("-updated_at", "id")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.milestone.MilestoneModel.objects")
    def test_list_milestones_with_organization_filter(self, mock_objects):
        """Test listing milestones with only organization filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = "OWASP"
        mock_filters.repository = None
        mock_filters.state = None

        mock_select_related = MagicMock()
        mock_filter_org = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filter_org
        mock_filter_org.order_by.return_value = mock_ordered

        result = list_milestones(mock_request, filters=mock_filters, ordering=None)

        mock_select_related.filter.assert_called_once_with(
            repository__organization__login__iexact="OWASP"
        )
        mock_filter_org.order_by.assert_called_once_with("-created_at", "-updated_at", "id")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.milestone.MilestoneModel.objects")
    def test_list_milestones_with_repository_filter(self, mock_objects):
        """Test listing milestones with only repository filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = "Nest"
        mock_filters.state = None

        mock_select_related = MagicMock()
        mock_filter_repo = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filter_repo
        mock_filter_repo.order_by.return_value = mock_ordered

        result = list_milestones(mock_request, filters=mock_filters, ordering=None)

        mock_select_related.filter.assert_called_once_with(repository__name__iexact="Nest")
        mock_filter_repo.order_by.assert_called_once_with("-created_at", "-updated_at", "id")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.milestone.MilestoneModel.objects")
    def test_list_milestones_with_state_filter(self, mock_objects):
        """Test listing milestones with only state filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = None
        mock_filters.state = "closed"

        mock_select_related = MagicMock()
        mock_filter_state = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select_related
        mock_select_related.filter.return_value = mock_filter_state
        mock_filter_state.order_by.return_value = mock_ordered

        result = list_milestones(mock_request, filters=mock_filters, ordering=None)

        mock_select_related.filter.assert_called_once_with(state="closed")
        mock_filter_state.order_by.assert_called_once_with("-created_at", "-updated_at", "id")
        assert result == mock_ordered


class TestGetMilestone:
    """Test cases for get_milestone endpoint."""

    @patch("apps.api.rest.v0.milestone.MilestoneModel.objects")
    def test_get_milestone_found(self, mock_objects):
        """Test getting a milestone that exists."""
        mock_request = MagicMock()
        mock_milestone = MagicMock()

        mock_objects.get.return_value = mock_milestone

        result = get_milestone(
            mock_request,
            organization_id="OWASP",
            repository_id="Nest",
            milestone_id=1,
        )

        mock_objects.get.assert_called_once_with(
            repository__organization__login__iexact="OWASP",
            repository__name__iexact="Nest",
            number=1,
        )
        assert result == mock_milestone

    @patch("apps.api.rest.v0.milestone.MilestoneModel.objects")
    def test_get_milestone_not_found(self, mock_objects):
        """Test getting a milestone that does not exist returns 404."""
        mock_request = MagicMock()

        mock_objects.get.side_effect = MilestoneModel.DoesNotExist

        result = get_milestone(
            mock_request,
            organization_id="OWASP",
            repository_id="NonExistent",
            milestone_id=999,
        )

        mock_objects.get.assert_called_once_with(
            repository__organization__login__iexact="OWASP",
            repository__name__iexact="NonExistent",
            number=999,
        )
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert b"Milestone not found" in result.content
