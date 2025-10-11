from unittest.mock import patch

import pytest

from apps.owasp.index.search.chapter import get_chapters

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
        "apps.owasp.index.search.chapter.raw_search", return_value=expected_hits
    ) as mock_raw_search:
        result = get_chapters(query=query, page=int(page))

        mock_raw_search.assert_called_once()
        assert result == expected_hits
