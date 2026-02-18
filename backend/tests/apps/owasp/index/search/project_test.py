from unittest.mock import patch

import pytest

from apps.owasp.index.search.project import get_projects

MOCKED_HITS = {
    ("hits"): [
        {"idx_name": "OWASP Amass", "idx_url": "https://owasp.org/www-project-amass/"},
        {"idx_name": "OWASP Juice Shop", "idx_url": "https://owasp.org/www-project-juice-shop/"},
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
def test_get_projects(query, page, expected_hits):
    with patch(
        "apps.owasp.index.search.project.raw_search", return_value=expected_hits
    ) as mock_raw_search:
        result = get_projects(query=query, page=page)

        mock_raw_search.assert_called_once()
        assert result == expected_hits


def test_get_projects_with_searchable_attributes():
    with patch(
        "apps.owasp.index.search.project.raw_search", return_value=MOCKED_HITS
    ) as mock_raw_search:
        result = get_projects(query="test", searchable_attributes=["idx_name"])

        mock_raw_search.assert_called_once()
        call_args = mock_raw_search.call_args[0]
        params = call_args[2]
        assert params["restrictSearchableAttributes"] == ["idx_name"]
        assert result == MOCKED_HITS
