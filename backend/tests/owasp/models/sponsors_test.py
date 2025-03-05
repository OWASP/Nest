from unittest.mock import Mock, patch

import pytest

from apps.owasp.models.sponsor import Sponsor


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
            ("Diamond", "Diamond"),
            ("Platinum", "Platinum"),
            ("Gold", "Gold"),
            ("Silver", "Silver"),
            ("Supporter", "Supporter"),
            ("Not a Sponsor", "Not Sponsor"),
        ],
    )
    def test_readable_sponsor_type(self, sponsor_type, expected_label):
        """Test the readable_sponsor_type property."""
        sponsor = Sponsor(sponsor_type=sponsor_type)
        assert sponsor.readable_sponsor_type == expected_label

    @pytest.mark.parametrize(
        ("member_type", "expected_label"),
        [
            ("Platinum", "Platinum"),
            ("Gold", "Gold"),
            ("Silver", "Silver"),
        ],
    )
    def test_readable_member_type(self, member_type, expected_label):
        """Test the readable_member_type property."""
        sponsor = Sponsor(member_type=member_type)
        assert sponsor.readable_member_type == expected_label

    def test_bulk_save(self):
        """Test the bulk_save method."""
        mock_sponsors = [Mock(id=None), Mock(id=1)]
        with patch("apps.owasp.models.sponsor.BulkSaveModel.bulk_save") as mock_bulk_save:
            Sponsor.bulk_save(mock_sponsors, fields=["name"])
            mock_bulk_save.assert_called_once_with(Sponsor, mock_sponsors, fields=["name"])

    @pytest.mark.parametrize(
        ("sponsor_type_value", "expected_sponsor_type"),
        [
            (-1, "Not a Sponsor"),
            (1, "Diamond"),
            (2, "Platinum"),
        ],
    )
    def test_from_dict_sponsor_type_mapping(self, sponsor_type_value, expected_sponsor_type):
        """Test the from_dict method for sponsor_type mapping."""
        sponsor = Sponsor()
        sponsor.from_dict(
            {
                "name": "Sponsor",
                "sponsor": sponsor_type_value,
            }
        )
        assert sponsor.sponsor_type == expected_sponsor_type

    @pytest.mark.parametrize(
        ("member_type_value", "expected_member_type"),
        [
            (2, "Platinum"),
            (3, "Gold"),
            (4, "Silver"),
        ],
    )
    def test_from_dict_member_type_mapping(self, member_type_value, expected_member_type):
        """Test the from_dict method for member_type mapping."""
        sponsor = Sponsor()
        sponsor.from_dict(
            {
                "membertype": member_type_value,
                "name": "Sponsor",
            }
        )
        assert sponsor.member_type == expected_member_type
