from unittest.mock import MagicMock

import pytest

from apps.api.rest.v0.common import LocationFilter, Person


class TestLocationFilter:
    @pytest.mark.parametrize(
        "location_data",
        [
            {
                "latitude_gte": -5.0,
                "latitude_lte": 5.0,
                "longitude_gte": -10.0,
                "longitude_lte": 10.0,
            },
            {
                "latitude_gte": 15.0,
                "latitude_lte": 25.0,
                "longitude_gte": 20.0,
                "longitude_lte": 30.0,
            },
        ],
    )
    def test_location_filter_validation(self, location_data):
        location_filter = LocationFilter(**location_data)

        assert location_filter.latitude_gte == location_data["latitude_gte"]
        assert location_filter.latitude_lte == location_data["latitude_lte"]
        assert location_filter.longitude_gte == location_data["longitude_gte"]
        assert location_filter.longitude_lte == location_data["longitude_lte"]


class TestPerson:
    """Tests for the Person schema."""

    def test_resolve_name_uses_login_when_matched(self):
        """Prefer the matched User login when member_id is set."""
        entity = MagicMock()
        entity.id = 1
        entity.member_id = 42
        entity.member.login = "john_doe"
        entity.member_name = "John Doe"

        ref = Person.from_orm(entity)

        assert ref.id == 1
        assert ref.name == "john_doe"

    def test_resolve_name_falls_back_to_member_name(self):
        """Fall back to member_name when no matched User exists."""
        entity = MagicMock()
        entity.id = 2
        entity.member_id = None
        entity.member_name = "Jane Director"

        ref = Person.from_orm(entity)

        assert ref.id == 2
        assert ref.name == "Jane Director"
