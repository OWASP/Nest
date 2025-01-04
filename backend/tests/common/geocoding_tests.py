from unittest.mock import MagicMock, patch

import pytest

from apps.common.geocoding import get_ip_coordinates, get_location_coordinates


class TestGeocoding:
    @pytest.mark.parametrize(
        ("ip_address", "mock_status_code", "mock_text", "expected_result"),
        [
            ("8.8.8.8", 200, "37.7749,-122.4194", ["37.7749", "-122.4194"]),
            ("invalid_ip", 404, "", None),
        ],
    )
    @patch("apps.common.geocoding.requests.get")
    def test_get_ip_coordinates(
        self, mock_get, ip_address, mock_status_code, mock_text, expected_result
    ):
        mock_response = MagicMock()
        mock_response.status_code = mock_status_code
        mock_response.text = mock_text
        mock_get.return_value = mock_response

        result = get_ip_coordinates(ip_address)
        assert result == expected_result

    @pytest.mark.parametrize(
        ("query", "mock_latitude", "mock_longitude"),
        [
            ("San Francisco, CA", 37.7749, -122.4194),
        ],
    )
    @patch("apps.common.geocoding.Nominatim.geocode")
    @patch("apps.common.geocoding.get_nest_user_agent", return_value="test_agent")
    def test_get_location_coordinates(
        self, mock_get_nest_user_agent, mock_geocode, query, mock_latitude, mock_longitude
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
