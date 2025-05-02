from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from django.conf import settings

from apps.common.utils import (
    get_absolute_url,
    get_nest_user_agent,
    get_user_ip_address,
    join_values,
    natural_date,
    natural_number,
    slugify,
    truncate,
)


class TestUtils:
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
            (datetime(2025, 1, 2, tzinfo=timezone.utc), 1),
            (int(datetime(2025, 1, 2, tzinfo=timezone.utc).timestamp()), 1),
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

    @patch("apps.common.utils.settings")
    def test_get_nest_user_agent(self, mock_settings):
        mock_settings.APP_NAME = "Test App"
        assert get_nest_user_agent() == "test-app"

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("Hello World", "hello-world"),
            ("Test--with---many-dashes", "test-with-many-dashes"),
            ("Special Characters!@#", "special-characters"),
        ],
    )
    def test_slugify(self, text, expected):
        assert slugify(text) == expected

    @pytest.mark.parametrize(
        ("text", "limit", "truncate_text", "expected"),
        [
            ("This is a long text", 10, "...", "This is..."),
            ("Short", 10, "...", "Short"),
            ("Another long text", 5, "***", "An***"),
        ],
    )
    def test_truncate(self, text, limit, truncate_text, expected):
        assert truncate(text, limit, truncate=truncate_text) == expected

    @pytest.mark.parametrize(
        ("meta_dict", "expected_ip"),
        [
            ({"HTTP_X_FORWARDED_FOR": "192.168.1.1,10.0.0.1"}, "192.168.1.1"),
            ({"HTTP_X_FORWARDED_FOR": "192.168.1.1"}, "192.168.1.1"),
            ({"REMOTE_ADDR": "192.168.1.1"}, "192.168.1.1"),
            ({"HTTP_X_FORWARDED_FOR": None, "REMOTE_ADDR": "192.168.1.1"}, "192.168.1.1"),
        ],
    )
    def test_get_user_ip_address(self, meta_dict, expected_ip):
        mock_request = type("Request", (), {"META": meta_dict})
        assert get_user_ip_address(mock_request) == expected_ip

    @pytest.mark.parametrize(
        ("value", "expected_format"),
        [
            ("2025-01-01", str),
            (datetime(2025, 1, 2, tzinfo=timezone.utc), str),
            (int(datetime(2025, 1, 2, tzinfo=timezone.utc).timestamp()), str),
        ],
    )
    def test_natural_date_return_format(self, value, expected_format):
        result = natural_date(value)
        assert isinstance(result, expected_format)
        assert len(result) > 0
