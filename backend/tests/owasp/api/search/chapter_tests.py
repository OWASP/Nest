from unittest.mock import patch

import pytest

from apps.owasp.api.search.chapter import get_chapters

MOCKED_COORDINATES = (37.7749, -122.4194)
MOCKED_USER_IP = "127.0.0.1"
MOCKED_HITS = {
    ("hits"): [
        {"idx_name": "OWASP San Francisco", "idx_url": "https://owasp.org/www-chapter-nagoya/"},
        {"idx_name": "OWASP New York", "idx_url": "https://owasp.org/www-chapter-seoul/"},
    ],
    ("nbPages"): 5,
}


@pytest.mark.parametrize(
    ("query", "page", "expected_hits"),
    [
        ("security", "1", MOCKED_HITS),
        ("web", "2", MOCKED_HITS),
        ("", "1", MOCKED_HITS),
    ],
)
def test_get_chapters(query, page, expected_hits):
    with patch(
        "apps.owasp.api.search.chapter.raw_search", return_value=expected_hits
    ) as mock_raw_search:
        result = get_chapters(query=query, meta={"REMOTE_ADDR": MOCKED_USER_IP}, page=int(page))

        mock_raw_search.assert_called_once()
        assert result == expected_hits
