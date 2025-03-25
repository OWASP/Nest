from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import os

import pytest
from django.conf import settings

from apps.common.utils import (
    get_absolute_url,
    get_user_ip_address,
    join_values,
    natural_date,
    natural_number,
)

PUBLIC_DNS_IP = os.environ.get("PUBLIC_DNS_IP")
PUBLIC_IP_ADDRESS = os.environ.get("PUBLIC_IP_ADDRESS")


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

    @pytest.mark.parametrize(
        ("mock_request", "expected"),
        [
            ({"https_X_FORWARDED_FOR": PUBLIC_DNS_IP}, PUBLIC_DNS_IP),
            ({"REMOTE_ADDR": PUBLIC_IP_ADDRESS}, PUBLIC_IP_ADDRESS),
        ],
    )
    def test_get_user_ip_address(self, mock_request, expected):
        request = MagicMock()
        request.META = mock_request
        assert get_user_ip_address(request) == expected

    def test_get_user_ip_address_local(self, mocker):
        request = MagicMock()
        request.META = {}

        mocker.patch.object(settings, "ENVIRONMENT", "Local")
        mocker.patch.dict(settings._wrapped.__dict__, {"PUBLIC_IP_ADDRESS": "1.1.1.1"})

        assert get_user_ip_address(request) == "1.1.1.1"