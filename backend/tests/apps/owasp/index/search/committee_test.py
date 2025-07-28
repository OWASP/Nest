from unittest.mock import patch

import pytest

from apps.owasp.index.search.committee import get_committees

MOCKED_HITS = {
    ("hits"): [
        {
            "idx_name": "OWASP Education and Training Committee",
            "idx_url": "https://owasp.org/www-committee-education-and-training/",
        },
        {
            "idx_name": "OWASP Chapter Committee",
            "idx_url": "https://owasp.org/www-committee-chapter/",
        },
    ],
    ("nbPages"): 5,
}


@pytest.mark.parametrize(
    ("query", "page", "expected_hits"),
    [
        ("security", 1, MOCKED_HITS),
        ("web", 2, MOCKED_HITS),
        ("", 1, MOCKED_HITS),
    ],
)
def test_get_committees(query, page, expected_hits):
    with patch(
        "apps.owasp.index.search.committee.raw_search", return_value=expected_hits
    ) as mock_raw_search:
        result = get_committees(query=query, page=page)

        mock_raw_search.assert_called_once()
        assert result == expected_hits
