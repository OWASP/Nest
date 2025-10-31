from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.committee import CommitteeDetail, get_chapter, list_committees


@pytest.mark.parametrize(
    "committee_data",
    [
        {
            "created_at": "2024-11-01T00:00:00Z",
            "description": "A test committee",
            "key": "test-committee",
            "name": "Test Committee",
            "updated_at": "2024-07-02T00:00:00Z",
        },
        {
            "created_at": "2023-12-01T00:00:00Z",
            "description": "A committee without a name",
            "key": "this-is-a-committee",
            "name": "this is a committee",
            "updated_at": "2023-09-02T00:00:00Z",
        },
    ],
)
def test_committee_serializer_validation(committee_data):
    class MockCommittee:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
            self.nest_key = data["key"]

    committee = CommitteeDetail.from_orm(MockCommittee(committee_data))

    assert committee.created_at == datetime.fromisoformat(committee_data["created_at"])
    assert committee.description == committee_data["description"]
    assert committee.key == committee_data["key"]
    assert committee.name == committee_data["name"]
    assert committee.updated_at == datetime.fromisoformat(committee_data["updated_at"])


class TestListCommittees:
    """Test cases for list_committees endpoint."""

    @patch("apps.api.rest.v0.committee.CommitteeModel.active_committees")
    def test_list_committees_with_ordering(self, mock_active_committees):
        """Test listing committees with custom ordering."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()

        mock_active_committees.order_by.return_value = mock_queryset

        result = list_committees(mock_request, ordering="created_at")

        mock_active_committees.order_by.assert_called_once_with("created_at")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.committee.CommitteeModel.active_committees")
    def test_list_committees_with_default_ordering(self, mock_active_committees):
        """Test that None ordering triggers default '-created_at' ordering."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()

        mock_active_committees.order_by.return_value = mock_queryset

        result = list_committees(mock_request, ordering=None)

        mock_active_committees.order_by.assert_called_once_with("-created_at")
        assert result == mock_queryset


class TestGetCommittee:
    """Test cases for get_committee endpoint."""

    @patch("apps.api.rest.v0.committee.CommitteeModel.active_committees")
    def test_get_committee_with_prefix(self, mock_active_committees):
        """Test getting a committee when committee_id already has www-committee- prefix."""
        mock_request = MagicMock()
        mock_committee = MagicMock()
        mock_filter = MagicMock()

        mock_active_committees.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_committee

        result = get_chapter(mock_request, committee_id="www-committee-project")

        mock_active_committees.filter.assert_called_once_with(
            is_active=True, key__iexact="www-committee-project"
        )
        mock_filter.first.assert_called_once()
        assert result == mock_committee

    @patch("apps.api.rest.v0.committee.CommitteeModel.active_committees")
    def test_get_committee_without_prefix(self, mock_active_committees):
        """Test getting a committee when committee_id needs www-committee- prefix added."""
        mock_request = MagicMock()
        mock_committee = MagicMock()
        mock_filter = MagicMock()

        mock_active_committees.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_committee

        result = get_chapter(mock_request, committee_id="project")

        mock_active_committees.filter.assert_called_once_with(
            is_active=True, key__iexact="www-committee-project"
        )
        mock_filter.first.assert_called_once()
        assert result == mock_committee

    @patch("apps.api.rest.v0.committee.CommitteeModel.active_committees")
    def test_get_committee_not_found(self, mock_active_committees):
        """Test getting a committee that does not exist returns 404."""
        mock_request = MagicMock()
        mock_filter = MagicMock()

        mock_active_committees.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = get_chapter(mock_request, committee_id="nonexistent")

        mock_active_committees.filter.assert_called_once_with(
            is_active=True, key__iexact="www-committee-nonexistent"
        )
        mock_filter.first.assert_called_once()
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert b"Committee not found" in result.content

    @patch("apps.api.rest.v0.committee.CommitteeModel.active_committees")
    def test_get_committee_uppercase_prefix(self, mock_active_committees):
        """Test that uppercase prefix is not detected and gets added again."""
        mock_request = MagicMock()
        mock_filter = MagicMock()

        mock_active_committees.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = get_chapter(mock_request, committee_id="WWW-COMMITTEE-Project")

        mock_active_committees.filter.assert_called_once_with(
            is_active=True, key__iexact="www-committee-WWW-COMMITTEE-Project"
        )
        mock_filter.first.assert_called_once()
        assert result.status_code == HTTPStatus.NOT_FOUND
