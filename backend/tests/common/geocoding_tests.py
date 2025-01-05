from unittest.mock import MagicMock, patch

import pytest

from apps.common.geocoding import get_location_coordinates


class TestGeocoding:
    @pytest.mark.parametrize(
        ("query", "mock_latitude", "mock_longitude"),
        [
            ("San Francisco, CA", 37.7749, -122.4194),
        ],
    )
    @patch("apps.common.geocoding.time.sleep", return_value=None)
    @patch("apps.common.geocoding.Nominatim.geocode")
    @patch("apps.common.geocoding.get_nest_user_agent", return_value="test_agent")
    def test_get_location_coordinates(
        self,
        mock_get_nest_user_agent,
        mock_geocode,
        mock_sleep,
        query,
        mock_latitude,
        mock_longitude,
    ):
        mock_geocode.return_value = MagicMock(latitude=mock_latitude, longitude=mock_longitude)

        result = get_location_coordinates(query)
        assert result.latitude == mock_latitude
        assert result.longitude == mock_longitude

    @patch("apps.common.geocoding.time.sleep", return_value=None)
    @patch("apps.common.geocoding.Nominatim.geocode", return_value=None)
    @patch("apps.common.geocoding.get_nest_user_agent", return_value="test_agent")
    def test_get_location_coordinates_none(
        self, mock_get_nest_user_agent, mock_geocode, mock_sleep
    ):
        query = "Invalid Location"
        result = get_location_coordinates(query)
        assert result is None
