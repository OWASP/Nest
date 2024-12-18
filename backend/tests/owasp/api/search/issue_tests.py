import json
from unittest.mock import patch

import pytest
import requests
from django.http import HttpRequest, JsonResponse

from apps.github.models.issue import Issue
from apps.owasp.api.search.issue import get_issues, project_issues

# Test data for parametrized tests
MOCKED_HITS = {
    ("hits"): [
        {"idx_project_name": "OWASP CycloneDX","idx_project_url":"https://owasp.org/www-project-cyclonedx/","idx_title": "string contains null byte", "idx_url": "https://github.com/CycloneDX/cyclonedx-cocoapods/issues/85"},
        {"idx_project_name": "OWASP Nest","idx_project_url":"https://owasp.org/www-project-nest/","idx_name": "Increase slackbot test coverage", "idx_url": "https://github.com/OWASP/Nest/issues/193"},
    ],
    ("nbPages"): 4,
}


@pytest.mark.parametrize(
    ("query", "page", "expected_hits"),
    [
        ("security", 1, MOCKED_HITS),
        ("web", 2, MOCKED_HITS),
        ("", 1, MOCKED_HITS),  # Edge case: empty query
    ],
)
def test_get_issues(query, page, expected_hits):
    # Use context managers for mocking
    with patch(
        "apps.owasp.api.search.issue.raw_search", return_value=expected_hits
    ) as mock_raw_search:
        # Call function
        result = get_issues(query, page=page, distinct=False)

        # Assertions
        mock_raw_search.assert_called_once()
        assert result == expected_hits


@pytest.mark.parametrize(
    ("query", "page", "expected_response"),
    [
        (
            "security",
            1,
            {
                "open_issues_count": 10,
                "issues": MOCKED_HITS["hits"],
                "total_pages": MOCKED_HITS["nbPages"],
            },
        ),
    ],
)
def test_issues(query, page, expected_response):
    # Create a mock request
    request = HttpRequest()
    request.GET = {"q": query, "page": str(page)}

    # Use context managers for mocking
    with (
        patch.object(Issue, "open_issues_count", return_value=10) as mock_active_count,
        patch(
            "apps.owasp.api.search.issue.get_issues", return_value=MOCKED_HITS
        ) as mock_get_issues,
    ):
        # Call function
        response = project_issues(request)

        # Assertions
        assert isinstance(response, JsonResponse)
        assert response.status_code == requests.codes.ok

        # Parse the JSON content instead of using .json()
        response_data = json.loads(response.content)
        assert response_data == expected_response

        # Verify mock calls
        mock_get_issues.assert_called_once_with(query, page=page, distinct=False)
        mock_active_count.assert_called_once()
