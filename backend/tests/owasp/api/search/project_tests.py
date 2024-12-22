import json
from unittest.mock import patch

import pytest
import requests
from django.http import HttpRequest, JsonResponse

from apps.common.index import IndexBase
from apps.owasp.api.search.project import get_projects, projects

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
        "apps.owasp.api.search.project.raw_search", return_value=expected_hits
    ) as mock_raw_search:
        result = get_projects(query=query, page=page)

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
    request = HttpRequest()
    request.GET = {"q": query, "page": str(page)}

    with (
        patch.object(IndexBase, "get_total_count", return_value=10) as mock_active_count,
        patch(
            "apps.owasp.api.search.project.get_projects", return_value=MOCKED_HITS
        ) as mock_get_projects,
    ):
        response = projects(request)

        assert isinstance(response, JsonResponse)
        assert response.status_code == requests.codes.ok

        response_data = json.loads(response.content)
        assert response_data == expected_response

        mock_get_projects.assert_called_once_with(
            query=query,
            page=page,
        )
        mock_active_count.assert_called_once()
