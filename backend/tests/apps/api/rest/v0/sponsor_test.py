from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.sponsor import SponsorDetail, get_sponsor, list_sponsors


class TestSponsorSchema:
    @pytest.mark.parametrize(
        "sponsor_data",
        [
            {
                "description": "A top-tier gold sponsor.",
                "image_url": "https://cdn.com/gold.png",
                "is_member": True,
                "job_url": "https://goldsponsor.com/jobs",
                "key": "gold-sponsor-inc.",
                "member_type": "PLATINUM",
                "name": "Gold Sponsor Inc.",
                "sponsor_type": "GOLD",
                "url": "https://goldsponsor.com",
            },
            {
                "description": "A reliable silver sponsor.",
                "image_url": "https://cdn.com/silver.png",
                "is_member": True,
                "job_url": "",
                "key": "silver-sponsor-llc",
                "member_type": "SILVER",
                "name": "Silver Sponsor LLC",
                "sponsor_type": "SILVER",
                "url": "https://silversponsor.com",
            },
        ],
    )
    def test_sponsor_schema_creation(self, sponsor_data):
        """Test schema creation with valid data."""
        sponsor = SponsorDetail(**sponsor_data)

        assert sponsor.description == sponsor_data["description"]
        assert sponsor.image_url == sponsor_data["image_url"]
        assert sponsor.is_member == sponsor_data["is_member"]
        assert sponsor.job_url == sponsor_data["job_url"]
        assert sponsor.key == sponsor_data["key"]
        assert sponsor.member_type == sponsor_data["member_type"]
        assert sponsor.name == sponsor_data["name"]
        assert sponsor.sponsor_type == sponsor_data["sponsor_type"]
        assert sponsor.url == sponsor_data["url"]

    def test_sponsor_schema_with_minimal_data(self):
        """Test schema with minimal required fields."""
        minimal_data = {
            "description": "",
            "image_url": "",
            "is_member": False,
            "job_url": "",
            "key": "test-sponsor",
            "member_type": "",
            "name": "Test Sponsor",
            "sponsor_type": "SILVER",
            "url": "",
        }
        sponsor = SponsorDetail(**minimal_data)

        assert sponsor.job_url == ""
        assert sponsor.key == "test-sponsor"
        assert sponsor.name == "Test Sponsor"


class TestListSponsors:
    """Test cases for list_sponsors endpoint."""

    @patch("apps.api.rest.v0.sponsor.SponsorModel.objects")
    def test_list_sponsors_with_custom_ordering(self, mock_objects):
        """Test listing sponsors with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_ordered = MagicMock()
        mock_final = MagicMock()

        mock_objects.order_by.return_value = mock_ordered
        mock_filters.filter.return_value = mock_final

        result = list_sponsors(mock_request, filters=mock_filters, ordering="name")

        mock_objects.order_by.assert_called_once_with("name")
        mock_filters.filter.assert_called_once_with(mock_ordered)
        assert result == mock_final

    @patch("apps.api.rest.v0.sponsor.SponsorModel.objects")
    def test_list_sponsors_with_default_ordering(self, mock_objects):
        """Test listing sponsors with default ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_ordered = MagicMock()
        mock_final = MagicMock()

        mock_objects.order_by.return_value = mock_ordered
        mock_filters.filter.return_value = mock_final

        result = list_sponsors(mock_request, filters=mock_filters, ordering=None)

        mock_objects.order_by.assert_called_once_with("name")
        mock_filters.filter.assert_called_once_with(mock_ordered)
        assert result == mock_final

    @patch("apps.api.rest.v0.sponsor.SponsorModel.objects")
    def test_list_sponsors_with_reverse_ordering(self, mock_objects):
        """Test listing sponsors with reverse ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_ordered = MagicMock()
        mock_final = MagicMock()

        mock_objects.order_by.return_value = mock_ordered
        mock_filters.filter.return_value = mock_final

        result = list_sponsors(mock_request, filters=mock_filters, ordering="-name")

        mock_objects.order_by.assert_called_once_with("-name")
        mock_filters.filter.assert_called_once_with(mock_ordered)
        assert result == mock_final


class TestGetSponsor:
    """Test cases for get_sponsor endpoint."""

    @patch("apps.api.rest.v0.sponsor.SponsorModel.objects")
    def test_get_sponsor_found(self, mock_objects):
        """Test getting a sponsor that exists."""
        mock_request = MagicMock()
        mock_filter = MagicMock()
        mock_sponsor = MagicMock()

        mock_objects.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_sponsor

        result = get_sponsor(mock_request, sponsor_id="adobe")

        mock_objects.filter.assert_called_once_with(key__iexact="adobe")
        mock_filter.first.assert_called_once()
        assert result == mock_sponsor

    @patch("apps.api.rest.v0.sponsor.SponsorModel.objects")
    def test_get_sponsor_not_found(self, mock_objects):
        """Test getting a sponsor that does not exist returns 404."""
        mock_request = MagicMock()
        mock_filter = MagicMock()

        mock_objects.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = get_sponsor(mock_request, sponsor_id="nonexistent")

        mock_objects.filter.assert_called_once_with(key__iexact="nonexistent")
        mock_filter.first.assert_called_once()
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert b"Sponsor not found" in result.content
