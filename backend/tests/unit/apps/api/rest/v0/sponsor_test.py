from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from django.db import IntegrityError

from apps.api.rest.v0.sponsor import (
    SponsorDetail,
    apply_sponsor,
    get_sponsor,
    list_nest_sponsors,
    list_sponsors,
)


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
                "status": "active",
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
                "status": "active",
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
        assert sponsor.status == sponsor_data["status"]
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
            "status": "draft",
            "url": "",
        }
        sponsor = SponsorDetail(**minimal_data)

        assert sponsor.job_url == ""
        assert sponsor.key == "test-sponsor"
        assert sponsor.name == "Test Sponsor"
        assert sponsor.status == "draft"


class TestListSponsors:
    """Tests for list_sponsors endpoint."""

    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    def test_list_sponsors_no_ordering(self, mock_sponsor_model):
        """Test listing sponsors without ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.status = None
        mock_queryset = MagicMock()
        mock_filtered_queryset = MagicMock()
        mock_sponsor_model.objects.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_filtered_queryset
        mock_filters.filter.return_value = mock_filtered_queryset

        result = list_sponsors(mock_request, mock_filters, ordering=None)

        mock_sponsor_model.objects.order_by.assert_called_with("name")
        mock_queryset.filter.assert_called_once_with(
            status=mock_sponsor_model.SponsorStatus.ACTIVE
        )
        assert result == mock_filtered_queryset

    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    def test_list_sponsors_with_ordering(self, mock_sponsor_model):
        """Test listing sponsors with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.status = None
        mock_queryset = MagicMock()
        mock_filtered_queryset = MagicMock()
        mock_sponsor_model.objects.order_by.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_filtered_queryset
        mock_filters.filter.return_value = mock_filtered_queryset

        result = list_sponsors(mock_request, mock_filters, ordering="-name")

        mock_sponsor_model.objects.order_by.assert_called_with("-name")
        assert result == mock_filtered_queryset

    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    def test_list_sponsors_with_status_filter(self, mock_sponsor_model):
        """Test listing sponsors with explicit status filter skips default filtering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.status = "draft"
        mock_queryset = MagicMock()
        mock_sponsor_model.objects.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_sponsors(mock_request, mock_filters, ordering=None)

        mock_sponsor_model.objects.order_by.assert_called_with("name")
        mock_queryset.filter.assert_not_called()
        assert result == mock_queryset


class TestListNestSponsors:
    """Tests for list_nest_sponsors endpoint."""

    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    def test_list_nest_sponsors(self, mock_sponsor_model):
        """Test that active sponsors are ordered by tier precedence then name."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()
        (
            mock_sponsor_model.objects.filter.return_value.annotate.return_value.order_by
        ).return_value = mock_queryset
        mock_queryset.__iter__ = MagicMock(return_value=iter([]))

        list_nest_sponsors(mock_request)

        mock_sponsor_model.objects.filter.assert_called_once_with(
            status=mock_sponsor_model.SponsorStatus.ACTIVE
        )
        (
            mock_sponsor_model.objects.filter.return_value.annotate.return_value.order_by
        ).assert_called_once_with("tier_order", "name")


class TestGetSponsor:
    """Tests for get_sponsor endpoint."""

    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    def test_get_sponsor_success(self, mock_sponsor_model):
        """Test getting a sponsor when found."""
        mock_request = MagicMock()
        mock_sponsor = MagicMock()
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

    @patch("apps.api.rest.v0.sponsor.transaction")
    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    @patch("apps.api.rest.v0.sponsor.slugify")
    def test_apply_sponsor_success(self, mock_slugify, mock_sponsor_model, mock_transaction):
        """Test successful sponsor application."""
        mock_request = MagicMock()
        mock_slugify.return_value = "test-org"
        mock_sponsor_model.SponsorStatus.DRAFT = "draft"
        mock_transaction.atomic.return_value.__enter__ = MagicMock(return_value=None)
        mock_transaction.atomic.return_value.__exit__ = MagicMock(return_value=False)

        payload = MagicMock()
        payload.organization_name = "Test Org"
        payload.website = "https://test.org"
        payload.contact_email = "sponsor@test.org"
        payload.message = "We'd like to sponsor OWASP."

        result = apply_sponsor(mock_request, payload)

        assert result.status_code == HTTPStatus.CREATED
        mock_sponsor_model.objects.create.assert_called_once_with(
            contact_email=payload.contact_email,
            description=payload.message,
            key="test-org",
            name=payload.organization_name,
            sort_name=payload.organization_name,
            status=mock_sponsor_model.SponsorStatus.DRAFT,
            url=payload.website,
        )

    @patch("apps.api.rest.v0.sponsor.transaction")
    @patch("apps.api.rest.v0.sponsor.SponsorModel")
    @patch("apps.api.rest.v0.sponsor.slugify")
    def test_apply_sponsor_duplicate(self, mock_slugify, mock_sponsor_model, mock_transaction):
        """Test sponsor application with duplicate organization name returns BAD_REQUEST."""
        mock_request = MagicMock()
        mock_slugify.return_value = "existing-org"
        mock_sponsor_model.SponsorStatus.DRAFT = "draft"
        mock_transaction.atomic.return_value.__enter__ = MagicMock(return_value=None)
        mock_transaction.atomic.return_value.__exit__ = MagicMock(return_value=False)
        mock_sponsor_model.objects.create.side_effect = IntegrityError

        payload = MagicMock()
        payload.organization_name = "Existing Org"
        payload.website = "https://existing.org"
        payload.contact_email = "sponsor@existing.org"
        payload.message = ""

        result = apply_sponsor(mock_request, payload)

        assert result.status_code == HTTPStatus.BAD_REQUEST

    @patch("apps.api.rest.v0.sponsor.slugify")
    def test_apply_sponsor_empty_key(self, mock_slugify):
        """Test sponsor application with org name that produces an empty slug."""
        mock_request = MagicMock()
        mock_slugify.return_value = ""

        payload = MagicMock()
        payload.organization_name = "!!!"

        result = apply_sponsor(mock_request, payload)

        assert result.status_code == HTTPStatus.BAD_REQUEST
