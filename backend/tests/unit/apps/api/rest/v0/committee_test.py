from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.committee import CommitteeDetail, get_committee, list_committees


class TestCommitteeSerializerValidation:
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
    def test_committee_serializer_validation(self, committee_data):
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
    """Tests for list_committees endpoint."""

    @patch("apps.api.rest.v0.committee.CommitteeModel")
    def test_list_committees_no_ordering(self, mock_committee_model):
        """Test listing committees without ordering."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()
        mock_committee_model.active_committees.order_by.return_value = mock_queryset

        result = list_committees(mock_request, ordering=None)

        mock_committee_model.active_committees.order_by.assert_called_with("-created_at")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.committee.CommitteeModel")
    def test_list_committees_with_ordering(self, mock_committee_model):
        """Test listing committees with custom ordering."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()
        mock_committee_model.active_committees.order_by.return_value = mock_queryset

        result = list_committees(mock_request, ordering="updated_at")

        mock_committee_model.active_committees.order_by.assert_called_with("updated_at")
        assert result == mock_queryset


class TestGetCommittee:
    """Tests for get_committee endpoint."""

    @patch("apps.api.rest.v0.committee.CommitteeModel")
    def test_get_committee_success(self, mock_committee_model):
        """Test getting a committee when found."""
        mock_request = MagicMock()
        mock_committee = MagicMock()
        mock_committee_model.active_committees.filter.return_value.first.return_value = (
            mock_committee
        )

        result = get_committee(mock_request, "project")

        mock_committee_model.active_committees.filter.assert_called_with(
            is_active=True, key__iexact="www-committee-project"
        )
        assert result == mock_committee

    @patch("apps.api.rest.v0.committee.CommitteeModel")
    def test_get_committee_with_prefix(self, mock_committee_model):
        """Test getting a committee with www-committee- prefix."""
        mock_request = MagicMock()
        mock_committee = MagicMock()
        mock_committee_model.active_committees.filter.return_value.first.return_value = (
            mock_committee
        )

        result = get_committee(mock_request, "www-committee-project")

        mock_committee_model.active_committees.filter.assert_called_with(
            is_active=True, key__iexact="www-committee-project"
        )
        assert result == mock_committee

    @patch("apps.api.rest.v0.committee.CommitteeModel")
    def test_get_committee_not_found(self, mock_committee_model):
        """Test getting a committee when not found."""
        mock_request = MagicMock()
        mock_committee_model.active_committees.filter.return_value.first.return_value = None

        result = get_committee(mock_request, "NonExistent")

        assert result.status_code == HTTPStatus.NOT_FOUND
