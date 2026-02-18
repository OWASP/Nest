from unittest.mock import patch

import pytest

from apps.owasp.index.search.issue import get_issues

MOCKED_HITS = {
    ("hits"): [
        {
            "idx_project_name": "OWASP CycloneDX",
            "idx_project_url": "https://owasp.org/www-project-cyclonedx/",
            "idx_title": "string contains null byte",
            "idx_url": "https://github.com/CycloneDX/cyclonedx-cocoapods/issues/85",
        },
        {
            "idx_project_name": "OWASP Nest",
            "idx_project_url": "https://owasp.org/www-project-nest/",
            "idx_name": "Increase slackbot test coverage",
            "idx_url": "https://github.com/OWASP/Nest/issues/193",
        },
    ],
    ("nbPages"): 4,
}


class TestGetIssues:
    @pytest.mark.parametrize(
        ("query", "page", "expected_hits"),
        [
            ("security", 1, MOCKED_HITS),
            ("web", 2, MOCKED_HITS),
            ("", 1, MOCKED_HITS),
        ],
    )
    def test_get_issues(self, query, page, expected_hits):
        with patch(
            "apps.owasp.index.search.issue.raw_search", return_value=expected_hits
        ) as mock_raw_search:
            result = get_issues(query, page=page, distinct=False)

            mock_raw_search.assert_called_once()
            assert result == expected_hits

    def test_get_issues_with_distinct(self):
        with patch(
            "apps.owasp.index.search.issue.raw_search", return_value=MOCKED_HITS
        ) as mock_raw_search:
            result = get_issues("test", distinct=True)

            mock_raw_search.assert_called_once()
            call_args = mock_raw_search.call_args[0]
            params = call_args[2]
            assert params["distinct"] == 1
            assert result == MOCKED_HITS
