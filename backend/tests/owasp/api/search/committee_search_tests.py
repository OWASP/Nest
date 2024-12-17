import json
from unittest.mock import patch

import pytest
from django.http import HttpRequest, JsonResponse

from apps.owasp.api.search.committee import committees, get_committees
from apps.owasp.models.committee import Committee

# Test data for parametrized tests
MOCKED_COORDINATES = (37.7749, -122.4194)
MOCKED_USER_IP = "127.0.0.1"
MOCKED_HITS = {
    ("hits"): [
        {"idx_name": "OWASP San Francisco", "idx_url": "https://owasp.sf"},
        {"idx_name": "OWASP New York", "idx_url": "https://owasp.ny"},
    ],
    ("nbPages"): 5,
}
STATUS_CODE_200 = 200


@pytest.mark.parametrize(
    ("query", "page", "expected_hits"),
    [
        ("security", 1, MOCKED_HITS),
        ("web", 2, MOCKED_HITS),
        ("", 1, MOCKED_HITS),  # Edge case: empty query
    ],
)
def test_get_committees(query, page, expected_hits):
    # Use context managers for mocking
    with patch(
        "apps.owasp.api.search.committee.raw_search", return_value=expected_hits
    ) as mock_raw_search:
        # Call function
        result = get_committees(query=query, page=page)

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
                "active_committees_count": 10,
                "committees": MOCKED_HITS["hits"],
                "total_pages": MOCKED_HITS["nbPages"],
            },
        ),
    ],
)
def test_committees(query, page, expected_response):
    # Create a mock request
    request = HttpRequest()
    request.GET = {"q": query, "page": str(page)}

    # Use context managers for mocking
    with (
        patch.object(Committee, "active_committees_count", return_value=10) as mock_active_count,
        patch(
            "apps.owasp.api.search.committee.get_committees", return_value=MOCKED_HITS
        ) as mock_get_committees,
    ):
        # Call function
        response = committees(request)

        # Assertions
        assert isinstance(response, JsonResponse)
        assert response.status_code == STATUS_CODE_200

        # Parse the JSON content instead of using .json()
        response_data = json.loads(response.content)
        assert response_data == expected_response

        # Verify mock calls
        mock_get_committees.assert_called_once_with(
            query=query,
            page=page,
        )
        mock_active_count.assert_called_once()
