import json
from unittest.mock import patch

import pytest
from django.http import HttpRequest, JsonResponse

from apps.owasp.api.search.chapter import chapters, get_chapters
from apps.owasp.models.chapter import Chapter

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
def test_get_chapters(query, page, expected_hits):
    # Use context managers for mocking
    with patch(
        "apps.owasp.api.search.chapter.raw_search", return_value=expected_hits
    ) as mock_raw_search:
        # Call function
        result = get_chapters(query=query, page=page, meta={"REMOTE_ADDR": MOCKED_USER_IP})

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
                "active_chapters_count": 10,
                "chapters": MOCKED_HITS["hits"],
                "total_pages": MOCKED_HITS["nbPages"],
            },
        ),
    ],
)
def test_chapters(query, page, expected_response):
    # Create a mock request
    request = HttpRequest()
    request.GET = {"q": query, "page": str(page)}
    request.META = {"REMOTE_ADDR": MOCKED_USER_IP}

    # Use context managers for mocking
    with (
        patch.object(Chapter, "active_chapters_count", return_value=10) as mock_active_count,
        patch(
            "apps.owasp.api.search.chapter.get_chapters", return_value=MOCKED_HITS
        ) as mock_get_chapters,
    ):
        # Call function
        response = chapters(request)

        # Assertions
        assert isinstance(response, JsonResponse)
        assert response.status_code == STATUS_CODE_200

        # Parse the JSON content instead of using .json()
        response_data = json.loads(response.content)
        assert response_data == expected_response

        # Verify mock calls
        mock_get_chapters.assert_called_once_with(query=query, page=page, meta=request.META)
        mock_active_count.assert_called_once()
