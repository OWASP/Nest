from unittest.mock import Mock, patch

import pytest
from backend.apps.owasp.models.sponsors import Sponsor
from django.core.exceptions import ValidationError


class TestSponsorModel:
    @pytest.mark.parametrize(
        ("name", "expected_str"),
        [
            ("Test Sponsor", "Test Sponsor"),
            ("", ""),
        ],
    )
    def test_str_representation(self, name, expected_str):
        """Test the __str__ method of the Sponsor model."""
        sponsor = Sponsor(name=name)
        assert str(sponsor) == expected_str

    @pytest.mark.parametrize(
        ("sponsor_type", "expected_label"),
        [
            ("1", "Diamond"),
            ("2", "Platinum"),
            ("3", "Gold"),
            ("4", "Silver"),
            ("5", "Supporter"),
            ("-1", "Not a Sponsor"),
        ],
    )
    def test_readable_sponsor_type(self, sponsor_type, expected_label):
        """Test the readable_sponsor_type property."""
        sponsor = Sponsor(sponsor_type=sponsor_type)
        assert sponsor.readable_sponsor_type == expected_label

    @pytest.mark.parametrize(
        ("member_type", "expected_label"),
        [
            ("2", "Platinum"),
            ("3", "Gold"),
            ("4", "Silver"),
        ],
    )
    def test_readable_member_type(self, member_type, expected_label):
        """Test the readable_member_type property."""
        sponsor = Sponsor(member_type=member_type)
        assert sponsor.readable_member_type == expected_label

    def test_is_indexable(self):
        """Test the is_indexable property."""
        sponsor = Sponsor()
        assert sponsor.is_indexable is True

    def test_bulk_save(self):
        """Test the bulk_save method."""
        mock_sponsors = [Mock(id=None), Mock(id=1)]
        with patch("apps.owasp.models.sponsor.BulkSaveModel.bulk_save") as mock_bulk_save:
            Sponsor.bulk_save(mock_sponsors, fields=["name"])
            mock_bulk_save.assert_called_once_with(Sponsor, mock_sponsors, fields=["name"])

    def test_update_data(self):
        """Test the update_data method."""
        mock_sponsor = Mock()
        mock_sponsor.id = 1
        mock_sponsor.name = "Old Name"
        mock_sponsor.sponsor_type = "1"

        with patch("apps.owasp.models.sponsor.Sponsor.objects.get", return_value=mock_sponsor):
            updated_sponsor = Sponsor.update_data(
                mock_sponsor.id, name="New Name", sponsor_type="2"
            )
            assert updated_sponsor.name == "New Name"
            assert updated_sponsor.sponsor_type == "2"

        with patch(
            "apps.owasp.models.sponsor.Sponsor.objects.get", side_effect=Sponsor.DoesNotExist
        ):
            non_existent_sponsor = Sponsor.update_data(9999, name="New Name")
            assert non_existent_sponsor is None

    @pytest.mark.parametrize(
        ("url", "is_valid"),
        [
            ("https://example.com", True),
            ("invalid-url", False),
        ],
    )
    def test_sponsor_validation(self, url, is_valid):
        """Test validation of Sponsor fields."""
        sponsor = Sponsor(
            name="Test Sponsor",
            sort_name="Sponsor",
            description="Test Description",
            url=url,
            job_url="https://jobs.example.com",
            image_path="/images/test.png",
            is_member=True,
            member_type="2",
            sponsor_type="1",
        )

        if is_valid:
            sponsor.full_clean()
        else:
            with pytest.raises(ValidationError):
                sponsor.full_clean()

    @pytest.mark.parametrize(
        ("sponsor_type", "expected_sponsor_type"),
        [
            ("1", "1"),  # DIAMOND
            ("2", "2"),  # PLATINUM
            ("-1", "-1"),  # NOT_SPONSOR
        ],
    )
    def test_sponsor_type_default(self, sponsor_type, expected_sponsor_type):
        """Test the default sponsor_type behavior."""
        sponsor = Sponsor(sponsor_type=sponsor_type)
        assert sponsor.sponsor_type == expected_sponsor_type
