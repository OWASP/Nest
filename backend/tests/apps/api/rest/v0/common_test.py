import pytest

from apps.api.rest.v0.common import LocationFilter


@pytest.mark.parametrize(
    "location_data",
    [
        {
            "longitude_gte": -10.0,
            "longitude_lte": 10.0,
            "latitude_gte": -5.0,
            "latitude_lte": 5.0,
        },
        {
            "longitude_gte": 20.0,
            "longitude_lte": 30.0,
            "latitude_gte": 15.0,
            "latitude_lte": 25.0,
        },
    ],
)
def test_location_filter_validation(location_data):
    location_filter = LocationFilter(**location_data)

    assert location_filter.longitude_gte == location_data["longitude_gte"]
    assert location_filter.longitude_lte == location_data["longitude_lte"]
    assert location_filter.latitude_gte == location_data["latitude_gte"]
    assert location_filter.latitude_lte == location_data["latitude_lte"]
