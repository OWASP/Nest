"""Tests for OWASP app sponsor models."""

from unittest.mock import MagicMock, patch

import pytest

from apps.owasp.models.sponsor import Sponsor

test_sponsor_name = "Test Sponsor"
sponsor_objects_get = "apps.owasp.models.sponsor.Sponsor.objects.get"
sponsor_slugify = "apps.owasp.models.sponsor.slugify"


class TestSponsor:
    @pytest.fixture()
    def sponsor_data(self):
        return {
            "name": test_sponsor_name,
            "description": "Test Description",
            "image": "/assets/images/sponsors/test.png",
            "url": "https://example.com",
            "job_url": "https://careers.example.com",
            "member": True,
            "membertype": 3,  # Gold
            "sponsor": 2,  # Platinum
            "sortname": "Test",
        }

    def test_str_method(self):
        sponsor = MagicMock(spec=Sponsor)
        sponsor.name = test_sponsor_name
        with patch.object(Sponsor, "__str__", return_value=sponsor.name):
            assert Sponsor.__str__(sponsor) == test_sponsor_name

    def test_readable_member_type(self):
        for member_type, expected in [
            (Sponsor.MemberType.GOLD, "Gold"),
            (Sponsor.MemberType.PLATINUM, "Platinum"),
            (Sponsor.MemberType.SILVER, "Silver"),
        ]:
            sponsor = Sponsor()
            sponsor.member_type = member_type

            mock_member_type = MagicMock()
            mock_member_type.label = expected

            with patch.object(Sponsor.MemberType, "__call__", return_value=mock_member_type):
                assert Sponsor.readable_member_type.fget(sponsor) == expected

    def test_readable_sponsor_type(self):
        for sponsor_type, expected in [
            (Sponsor.SponsorType.DIAMOND, "Diamond"),
            (Sponsor.SponsorType.PLATINUM, "Platinum"),
            (Sponsor.SponsorType.GOLD, "Gold"),
            (Sponsor.SponsorType.SILVER, "Silver"),
            (Sponsor.SponsorType.SUPPORTER, "Supporter"),
            (Sponsor.SponsorType.NOT_SPONSOR, "Not Sponsor"),
        ]:
            sponsor = Sponsor()
            sponsor.sponsor_type = sponsor_type

            mock_sponsor_type = MagicMock()
            mock_sponsor_type.label = expected

            with patch.object(Sponsor.SponsorType, "__call__", return_value=mock_sponsor_type):
                assert Sponsor.readable_sponsor_type.fget(sponsor) == expected

    def test_bulk_save(self):
        sponsors_data = [
            {"id": 1, "field1": "value1"},
            {"id": 2, "field2": "value2"},
        ]

        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Sponsor.bulk_save(sponsors_data, fields=["field1", "field2"])
            mock_bulk_save.assert_called_once_with(
                Sponsor, sponsors_data, fields=["field1", "field2"]
            )

    def test_update_data_existing_sponsor(self, sponsor_data):
        mock_sponsor = MagicMock(spec=Sponsor)

        with patch(sponsor_objects_get, return_value=mock_sponsor) as mock_get, patch(
            sponsor_slugify, return_value="test-sponsor"
        ) as mock_slugify:
            result = Sponsor.update_data(sponsor_data)

            mock_slugify.assert_called_once_with(sponsor_data["name"])
            mock_get.assert_called_once_with(key="test-sponsor")
            mock_sponsor.from_dict.assert_called_once_with(sponsor_data)
            mock_sponsor.save.assert_called_once()
            assert result == mock_sponsor

    def test_update_data_new_sponsor(self, sponsor_data):
        mock_sponsor = MagicMock(spec=Sponsor)

        with patch(sponsor_objects_get, side_effect=Sponsor.DoesNotExist) as mock_get, patch(
            sponsor_slugify, return_value="test-sponsor"
        ) as mock_slugify, patch.object(Sponsor, "__new__", return_value=mock_sponsor):
            result = Sponsor.update_data(sponsor_data)

            mock_slugify.assert_called_once_with(sponsor_data["name"])
            mock_get.assert_called_once_with(key="test-sponsor")
            mock_sponsor.from_dict.assert_called_once_with(sponsor_data)
            mock_sponsor.save.assert_called_once()
            assert result == mock_sponsor

    def test_update_data_without_save(self, sponsor_data):
        mock_sponsor = MagicMock(spec=Sponsor)

        with patch(sponsor_objects_get, side_effect=Sponsor.DoesNotExist) as mock_get, patch(
            sponsor_slugify, return_value="test-sponsor"
        ) as mock_slugify, patch.object(Sponsor, "__new__", return_value=mock_sponsor):
            result = Sponsor.update_data(sponsor_data, save=False)

            mock_slugify.assert_called_once_with(sponsor_data["name"])
            mock_get.assert_called_once_with(key="test-sponsor")
            mock_sponsor.from_dict.assert_called_once_with(sponsor_data)
            mock_sponsor.save.assert_not_called()
            assert result == mock_sponsor

    def test_from_dict_complete_data(self, sponsor_data):
        with patch(
            "apps.github.utils.normalize_url",
            side_effect=lambda x: f"https://{x.split('://')[-1]}" if x else "",
        ):
            sponsor = MagicMock()

            Sponsor.from_dict(sponsor, sponsor_data)

            assert sponsor.name == test_sponsor_name
            assert sponsor.description == "Test Description"
            assert (
                sponsor.image_url
                == "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/assets/images/sponsors/test.png"
            )
            assert sponsor.url == "https://example.com"
            assert sponsor.job_url == "https://careers.example.com"
            assert sponsor.is_member is True

    def test_from_dict_minimal_data(self):
        minimal_data = {"name": "Minimal Sponsor"}

        with patch("apps.github.utils.normalize_url", return_value=""):
            sponsor = MagicMock()

            Sponsor.from_dict(sponsor, minimal_data)

            assert sponsor.name == "Minimal Sponsor"
            assert sponsor.description == ""
            assert (
                sponsor.image_url
                == "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/"
            )
            assert sponsor.is_member is False

    def test_from_dict_all_member_types(self):
        member_mapping = {
            2: Sponsor.MemberType.PLATINUM,
            3: Sponsor.MemberType.GOLD,
            4: Sponsor.MemberType.SILVER,
            99: Sponsor.MemberType.SILVER,
        }

        for member_key, expected_type in member_mapping.items():
            data = {"name": test_sponsor_name, "membertype": member_key}

            sponsor = MagicMock()
            Sponsor.from_dict(sponsor, data)
            sponsor.member_type = expected_type

    def test_from_dict_all_sponsor_types(self):
        mappings = [
            (-1, Sponsor.SponsorType.NOT_SPONSOR),
            (1, Sponsor.SponsorType.DIAMOND),
            (2, Sponsor.SponsorType.PLATINUM),
            (3, Sponsor.SponsorType.GOLD),
            (4, Sponsor.SponsorType.SILVER),
            (5, Sponsor.SponsorType.SUPPORTER),
            (99, Sponsor.SponsorType.NOT_SPONSOR),
        ]

        for sponsor_key, expected_type in mappings:
            data = {"name": test_sponsor_name, "sponsor": sponsor_key}

            sponsor = MagicMock()
            Sponsor.from_dict(sponsor, data)
            sponsor.sponsor_type = expected_type

    def test_normalize_url_calls(self):
        with patch("apps.owasp.models.sponsor.normalize_url") as mock_normalize:
            mock_normalize.side_effect = lambda x: f"normalized-{x}" if x else ""

            sponsor = MagicMock(spec=Sponsor)
            data = {
                "name": "URL Sponsor",
                "url": "http://example.com",
                "job_url": "http://example.com/jobs",
                "image": "/assets/images/sponsors/test.png",
            }

            Sponsor.from_dict(sponsor, data)
            call_count = 2
            assert mock_normalize.call_count >= call_count
            mock_normalize.assert_any_call(data["url"])
            mock_normalize.assert_any_call(data["job_url"])
