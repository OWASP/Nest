import json
from unittest.mock import patch

import pytest
import requests
from django.http import HttpRequest, JsonResponse

from apps.owasp.api.search.project import get_projects, projects
from apps.owasp.models.project import Project

# Test data for parametrized tests
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
        ("", 1, MOCKED_HITS),  # Edge case: empty query
    ],
)
def test_get_projects(query, page, expected_hits):
    # Use context managers for mocking
    with patch(
        "apps.owasp.api.search.project.raw_search", return_value=expected_hits
    ) as mock_raw_search:
        # Call function
        result = get_projects(query=query, page=page)

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
                "active_projects_count": 10,
                "projects": MOCKED_HITS["hits"],
                "total_pages": MOCKED_HITS["nbPages"],
            },
        ),
    ],
)
def test_projects(query, page, expected_response):
    # Create a mock request
    request = HttpRequest()
    request.GET = {"q": query, "page": str(page)}

    # Use context managers for mocking
    with (
        patch.object(Project, "active_projects_count", return_value=10) as mock_active_count,
        patch(
            "apps.owasp.api.search.project.get_projects", return_value=MOCKED_HITS
        ) as mock_get_projects,
    ):
        # Call function
        response = projects(request)

        # Assertions
        assert isinstance(response, JsonResponse)
        assert response.status_code == requests.codes.ok

        # Parse the JSON content instead of using .json()
        response_data = json.loads(response.content)
        assert response_data == expected_response

        # Verify mock calls
        mock_get_projects.assert_called_once_with(
            query=query,
            page=page,
        )
        mock_active_count.assert_called_once()
