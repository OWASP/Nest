import pytest
from unittest.mock import patch
from apps.owasp.api.search.sponsor import get_sponsors

MOCKED_SPONSOR_HITS = {
    "hits": [
        {
            "idx_name": "Example Corp",
            "idx_sort_name": "EXAMPLE CORP",
            "idx_description": "A leading security company",
            "idx_url": "https://example.com",
            "idx_job_url": "https://example.com/careers",
            "idx_image_path": "/assets/images/sponsors/example.png",
            "idx_member_type": "Corporate",
            "idx_sponsor_type": "Gold",
            "idx_is_member": True
        },
        {
            "idx_name": "Security Plus",
            "idx_sort_name": "SECURITY PLUS",
            "idx_description": "Cybersecurity solutions provider",
            "idx_url": "https://securityplus.com",
            "idx_job_url": "https://securityplus.com/jobs",
            "idx_image_path": "/assets/images/sponsors/secplus.png",
            "idx_member_type": "Corporate",
            "idx_sponsor_type": "Silver",
            "idx_is_member": True
        }
    ],
    "nbPages": 3
}

@pytest.mark.parametrize(
    ("query", "limit", "page", "expected_hits"),
    [
        ("security", 25, 1, MOCKED_SPONSOR_HITS),
        ("example", 10, 2, MOCKED_SPONSOR_HITS),
        ("", 25, 1, MOCKED_SPONSOR_HITS),
    ],
)
def test_get_sponsors_basic_search(query, limit, page, expected_hits):
    """Test basic sponsor search with different queries and pagination."""
    with patch(
        "apps.owasp.api.search.sponsor.raw_search",
        return_value=expected_hits
    ) as mock_raw_search:
        result = get_sponsors(query, limit=limit, page=page)
        
        assert result == expected_hits
        
        mock_raw_search.assert_called_once()
        _, call_query, call_params = mock_raw_search.call_args[0]
        
        assert call_query == query
        assert call_params["hitsPerPage"] == limit
        assert call_params["page"] == page - 1

def test_get_sponsors_custom_attributes():
    """Test sponsor search with custom attributes to retrieve."""
    custom_attributes = ["idx_name", "idx_url"]
    
    with patch(
        "apps.owasp.api.search.sponsor.raw_search",
        return_value=MOCKED_SPONSOR_HITS
    ) as mock_raw_search:
        result = get_sponsors("test", attributes=custom_attributes)
        
        _, _, call_params = mock_raw_search.call_args[0]
        assert call_params["attributesToRetrieve"] == custom_attributes

def test_get_sponsors_default_parameters():
    """Test sponsor search with default parameters."""
    with patch(
        "apps.owasp.api.search.sponsor.raw_search",
        return_value=MOCKED_SPONSOR_HITS
    ) as mock_raw_search:
        result = get_sponsors("test")
        
        _, _, call_params = mock_raw_search.call_args[0]
        assert call_params["hitsPerPage"] == 25
        assert call_params["page"] == 0
        assert call_params["minProximity"] == 4
        assert call_params["typoTolerance"] == "min"
        assert isinstance(call_params["attributesToRetrieve"], list)
        assert len(call_params["attributesToRetrieve"]) > 0