import pytest

from apps.github.api.issue import IssueSerializer


@pytest.mark.parametrize(
    "issue_data",
    [
        {
            "title": "Test Issue 1",
            "body": "This is a test issue 1",
            "state": "open",
            "url": "http://example.com/issues/1",
            "created_at": "2024-12-30T00:00:00Z",
            "updated_at": "2024-12-30T00:00:00Z",
        },
        {
            "title": "Test Issue 2",
            "body": "This is a test issue 2",
            "state": "closed",
            "url": "http://example.com/issues/2",
            "created_at": "2024-12-29T00:00:00Z",
            "updated_at": "2024-12-30T00:00:00Z",
        },
    ],
)
def test_issue_serializer(issue_data):
    """Test the IssueSerializer with various issue data."""
    serializer = IssueSerializer(data=issue_data)
    assert serializer.is_valid()
    validated_data = serializer.validated_data
    # Convert datetime objects to ISO format strings for comparison
    validated_data["created_at"] = validated_data["created_at"].isoformat().replace("+00:00", "Z")
    validated_data["updated_at"] = validated_data["updated_at"].isoformat().replace("+00:00", "Z")
    assert validated_data == issue_data
