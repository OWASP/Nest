from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from django.conf import settings

from apps.common.utils import (
    get_absolute_url,
    join_values,
    natural_date,
    natural_number,
)


class TestUtils:
    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("some/view", "http://example.com/some/view"),
            ("another/view", "http://example.com/another/view"),
        ],
    )
    @patch.object(settings, "SITE_URL", "http://example.com")
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
