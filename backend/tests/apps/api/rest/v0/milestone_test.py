from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from ninja.responses import Response

from apps.api.rest.v0.milestone import (
    MilestoneDetail,
    MilestoneFilter,
    get_milestone,
    list_milestones,
)
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
    """Tests for list_milestones view function."""

    def test_list_milestones_no_filter(self, mocker):
        """Test listing milestones without filters."""
        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.order_by.return_value = []
        mocker.patch(
            "apps.api.rest.v0.milestone.MilestoneModel.objects",
            mock_qs,
        )

        request = MagicMock()
        filters = MilestoneFilter()
        list_milestones(request, filters, None)

        mock_qs.order_by.assert_called_once_with("-created_at", "-updated_at")

    def test_list_milestones_with_organization_filter(self, mocker):
        """Test listing milestones with organization filter."""
        mock_qs = MagicMock()
        mock_filtered = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_filtered
        mock_filtered.order_by.return_value = []
        mocker.patch(
            "apps.api.rest.v0.milestone.MilestoneModel.objects",
            mock_qs,
        )

        request = MagicMock()
        filters = MilestoneFilter(organization="OWASP")
        list_milestones(request, filters, None)

        mock_qs.filter.assert_called_with(repository__organization__login__iexact="OWASP")

    def test_list_milestones_with_repository_filter(self, mocker):
        """Test listing milestones with repository filter."""
        mock_qs = MagicMock()
        mock_filtered = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_filtered
        mock_filtered.filter.return_value = mock_filtered
        mock_filtered.order_by.return_value = []
        mocker.patch(
            "apps.api.rest.v0.milestone.MilestoneModel.objects",
            mock_qs,
        )

        request = MagicMock()
        filters = MilestoneFilter(organization="OWASP", repository="Nest")
        list_milestones(request, filters, None)

        mock_filtered.filter.assert_called_with(repository__name__iexact="Nest")

    def test_list_milestones_with_state_filter(self, mocker):
        """Test listing milestones with state filter."""
        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = []
        mocker.patch(
            "apps.api.rest.v0.milestone.MilestoneModel.objects",
            mock_qs,
        )

        request = MagicMock()
        filters = MilestoneFilter(state="open")
        list_milestones(request, filters, None)

        mock_qs.filter.assert_called_with(state="open")

    def test_list_milestones_with_ordering(self, mocker):
        """Test listing milestones with custom ordering."""
        mock_qs = MagicMock()
        mock_qs.select_related.return_value = mock_qs
        mock_qs.order_by.return_value = []
        mocker.patch(
            "apps.api.rest.v0.milestone.MilestoneModel.objects",
            mock_qs,
        )

        request = MagicMock()
        filters = MilestoneFilter()
        list_milestones(request, filters, "updated_at")

        mock_qs.order_by.assert_called_once_with("updated_at")


class TestGetMilestone:
    """Tests for get_milestone view function."""

    def test_get_milestone_success(self, mocker):
        """Test getting a specific milestone successfully."""
        mock_milestone = MagicMock()
        mock_qs = MagicMock()
        mock_qs.get.return_value = mock_milestone
        mocker.patch(
            "apps.api.rest.v0.milestone.MilestoneModel.objects",
            mock_qs,
        )

        request = MagicMock()
        result = get_milestone(request, "OWASP", "Nest", 1)

        assert result == mock_milestone
        mock_qs.get.assert_called_once_with(
            repository__organization__login__iexact="OWASP",
            repository__name__iexact="Nest",
            number=1,
        )

    def test_get_milestone_not_found(self, mocker):
        """Test getting a non-existent milestone."""
        mock_qs = MagicMock()
        mock_qs.get.side_effect = MilestoneModel.DoesNotExist
        mocker.patch(
            "apps.api.rest.v0.milestone.MilestoneModel.objects",
            mock_qs,
        )

        request = MagicMock()
        result = get_milestone(request, "OWASP", "NonExistent", 999)

        assert isinstance(result, Response)
        assert result.status_code == HTTPStatus.NOT_FOUND
