from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.utils import (
    clean_url,
    convert_to_camel_case,
    convert_to_snake_case,
    get_absolute_url,
    get_user_ip_address,
    join_values,
    natural_date,
    natural_number,
    round_down,
    validate_url,
)


class TestUtils:
    @pytest.mark.parametrize(
        ("input_text", "expected_output"),
        [
            ("simple", "simple"),
            ("my_variable", "myVariable"),
            ("long_variable_name", "longVariableName"),
            ("top_contributor_project", "topContributorProject"),
            ("_leading_underscore", "_leadingUnderscore"),
            ("trailing_underscore_", "trailingUnderscore"),
            ("multiple__underscores", "multipleUnderscores"),
            ("multiple__under___scores", "multipleUnderScores"),
            ("alreadyCamelCase", "alreadyCamelCase"),
        ],
    )
    def test_convert_to_camel_case(self, input_text, expected_output):
        assert convert_to_camel_case(input_text) == expected_output

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("", ""),
            ("A", "a"),
            ("a1_b2_c3", "a1_b2_c3"),
            ("A1B2C3", "a1_b2_c3"),
            ("AppHomeOpened", "app_home_opened"),
            ("Contribute", "contribute"),
            ("Gsoc", "gsoc"),
            ("some_view_with_numbers123", "some_view_with_numbers123"),
            ("SomeViewWithNumbers123", "some_view_with_numbers123"),
            ("TeamJoin", "team_join"),
        ],
    )
    def test_convert_to_snake_case(self, text, expected):
        assert convert_to_snake_case(text) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("some/view", "https://example.com/some/view"),
            ("another/view", "https://example.com/another/view"),
        ],
    )
    @patch.object(settings, "SITE_URL", "https://example.com")
    def test_get_absolute_url(self, path, expected):
        assert get_absolute_url(path) == expected

    @pytest.mark.parametrize(
        ("values", "delimiter", "expected"),
        [
            (("1", "2", "3"), " ", "1 2 3"),
            (("1", "2", "3"), ",", "1,2,3"),
        ],
    )
    def test_join_values(self, values, delimiter, expected):
        assert join_values(values, delimiter=delimiter) == expected

    @pytest.mark.parametrize(
        ("value", "expected_calls"),
        [
            ("2025-01-01", 1),
            (datetime(2025, 1, 2, tzinfo=UTC), 1),
            (int(datetime(2025, 1, 2, tzinfo=UTC).timestamp()), 1),
        ],
    )
    @patch("apps.common.utils.naturaltime")
    def test_natural_date(self, mock_naturaltime, value, expected_calls):
        natural_date(value)
        assert mock_naturaltime.call_count == expected_calls

    @pytest.mark.parametrize(
        ("value", "unit", "expected"),
        [
            (1000, None, "1.0 thousand"),
            (1000, "item", "1.0 thousand items"),
            (1, "item", "1 item"),
        ],
    )
    def test_natural_number(self, value, unit, expected):
        assert natural_number(value, unit=unit) == expected

    @pytest.mark.parametrize(
        ("mock_request", "expected"),
        [
            ({"HTTP_X_FORWARDED_FOR": "172.16.1.100"}, "172.16.1.100"),  # NOSONAR
            ({"REMOTE_ADDR": "192.168.1.200"}, "192.168.1.200"),  # NOSONAR
        ],
    )
    def test_get_user_ip_address(self, mock_request, expected):
        request = MagicMock()
        request.META = mock_request
        assert get_user_ip_address(request) == expected

    def test_get_user_ip_address_local(self, mocker):
        request = MagicMock()
        request.META = {}

        mocker.patch.object(settings, "IS_LOCAL_ENVIRONMENT", return_value=True)
        mocker.patch.dict(
            settings._wrapped.__dict__,
            {"PUBLIC_IP_ADDRESS": "10.0.0.100"},  # NOSONAR
        )

        assert get_user_ip_address(request) == "10.0.0.100"  # NOSONAR

    @pytest.mark.parametrize(
        ("value", "base", "expected"),
        [
            (100, 10, 100),
            (101, 10, 100),
            (123, 10, 120),
            (123, 100, 100),
            (1230, 10, 1230),
            (1230, 100, 1200),
            (1230, 1000, 1000),
            (126, 5, 125),
            (43, 10, 40),
            (430, 100, 400),
            (99, 10, 90),
        ],
    )
    def test_round_down(self, value, base, expected):
        assert round_down(value, base) == expected

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("https://example.com", "https://example.com"),
            ("https://example.com.", "https://example.com"),
            ("https://example.com,", "https://example.com"),
            ("https://example.com!", "https://example.com"),
            ("https://example.com?", "https://example.com"),
            ("https://example.com;", "https://example.com"),
            ("https://example.com:", "https://example.com"),
            ("  https://example.com  ", "https://example.com"),
            ("https://example.com/path", "https://example.com/path"),
            ("https://example.com/path?", "https://example.com/path"),
            ("https://example.com/path!", "https://example.com/path"),
            ("", None),
            (None, None),
            ("   ", None),
            ("https://", "https://"),
            ("not-a-url", "not-a-url"),
        ],
    )
    def test_clean_url(self, url, expected):
        """Test the clean_url function."""
        assert clean_url(url) == expected

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("https://example.com", True),
            ("http://example.com", True),
            ("https://example.com/path", True),
            ("https://example.com/path?query=1", True),
            ("https://example.com/path#fragment", True),
            ("https://subdomain.example.com", True),
            ("https://example.com:8080", True),
            ("https://example.com:8080/path", True),
            ("", False),
            (None, False),
            ("not-a-url", False),
            ("ftp://example.com", False),
            ("https://", False),
            ("http://", False),
            ("https://example", True),  # Valid single label domain
            ("https://example.", True),  # Valid with trailing dot
            ("https://example.com.", True),  # Valid with trailing dot
            ("https://192.168.1.1", True),  # Valid IP address
            ("https://[::1]", True),  # Valid IPv6 address
            ("https://example.com:99999", True),  # Valid port (urlparse accepts it)
            # Malformed netloc test cases (issue #3535)
            ("http://.", False),  # Just a dot
            ("https://.", False),  # Just a dot with https
            ("http:// ", False),  # Just a space
            ("https:// ", False),  # Just a space with https
            ("http://-", False),  # Just a hyphen
            ("https://-", False),  # Just a hyphen with https
            ("http://...", False),  # Multiple dots
            ("https://...", False),  # Multiple dots with https
            ("http://.-", False),  # Dot and hyphen
            ("https://.-", False),  # Dot and hyphen with https
            ("http://-.", False),  # Hyphen and dot
            ("https://-.", False),  # Hyphen and dot with https
        ],
    )
    def test_validate_url(self, url, expected):
        """Test the validate_url function."""
        result = validate_url(url)
        assert result == expected
