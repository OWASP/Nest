from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.sponsor import SponsorDetail, apply_sponsor, get_sponsor, list_sponsors


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
    """Tests for list_sponsors endpoint."""

    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    def test_list_sponsors_no_ordering(self, mock_sponsor_model):
        """Test listing sponsors without ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_sponsor_model.objects.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_sponsors(mock_request, mock_filters, ordering=None)

        mock_sponsor_model.objects.order_by.assert_called_with("name")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    def test_list_sponsors_with_ordering(self, mock_sponsor_model):
        """Test listing sponsors with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_sponsor_model.objects.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_sponsors(mock_request, mock_filters, ordering="-name")

        mock_sponsor_model.objects.order_by.assert_called_with("-name")
        assert result == mock_queryset


class TestGetSponsor:
    """Tests for get_sponsor endpoint."""

    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    def test_get_sponsor_success(self, mock_sponsor_model):
        """Test getting a sponsor when found."""
        mock_request = MagicMock()
        mock_sponsor = MagicMock()
        mock_sponsor.status = mock_sponsor_model.Status.ACTIVE
        mock_sponsor_model.objects.filter.return_value.first.return_value = mock_sponsor

        result = get_sponsor(mock_request, "adobe")

        mock_sponsor_model.objects.filter.assert_called_with(key__iexact="adobe")
        assert result == mock_sponsor

    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    def test_get_sponsor_not_found(self, mock_sponsor_model):
        """Test getting a sponsor when not found."""
        mock_request = MagicMock()
        mock_sponsor_model.objects.filter.return_value.first.return_value = None

        result = get_sponsor(mock_request, "nonexistent")

        assert result.status_code == HTTPStatus.NOT_FOUND


class TestApplySponsor:
    """Tests for apply_sponsor endpoint."""

    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    def test_apply_sponsor_rejects_unsluggable_name(self, mock_sponsor_model):
        """Reject organization names that slugify to an empty key."""
        mock_request = MagicMock()

        payload = MagicMock()
        payload.organization_name = "   !!!   "
        payload.contact_email = "contact@example.com"
        payload.website = ""
        payload.message = ""

        status, body = apply_sponsor(mock_request, payload)

        assert status == HTTPStatus.BAD_REQUEST
        assert body.message
        mock_sponsor_model.objects.create.assert_not_called()

    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    def test_apply_sponsor_strips_name_before_slugify_and_persist(self, mock_sponsor_model):
        """Strip whitespace so we persist the cleaned organization name."""
        mock_request = MagicMock()

        payload = MagicMock()
        payload.organization_name = "  Acme, Inc.  "
        payload.contact_email = "contact@acme.com"
        payload.website = "https://acme.com"
        payload.message = "Hello"

        mock_sponsor_model.objects.filter.return_value.exists.return_value = False

        status, body = apply_sponsor(mock_request, payload)

        assert status == HTTPStatus.CREATED
        assert body.key
        mock_sponsor_model.objects.create.assert_called_once()
        _, kwargs = mock_sponsor_model.objects.create.call_args
        assert kwargs["name"] == "Acme, Inc."
        assert kwargs["sort_name"] == "Acme, Inc."
