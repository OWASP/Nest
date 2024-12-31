import pytest

from apps.github.api.release import ReleaseSerializer


@pytest.mark.parametrize(
    "release_data",
    [
        {
            "name": "v1.0",
            "tag_name": "v1.0.0",
            "description": "First stable release",
            "created_at": "2024-12-30T00:00:00Z",
            "published_at": "2024-12-30T00:00:00Z",
        },
        {
            "name": "v1.1",
            "tag_name": "v1.1.0",
            "description": "Minor improvements and bug fixes",
            "created_at": "2024-12-29T00:00:00Z",
            "published_at": "2024-12-30T00:00:00Z",
        },
    ],
)
def test_release_serializer(release_data):
    """Test the ReleaseSerializer with various release data."""
    serializer = ReleaseSerializer(data=release_data)
    assert serializer.is_valid()
    validated_data = serializer.validated_data
    # Convert datetime objects to ISO format strings for comparison
    validated_data["created_at"] = validated_data["created_at"].isoformat().replace("+00:00", "Z")
    validated_data["published_at"] = (
        validated_data["published_at"].isoformat().replace("+00:00", "Z")
    )
    assert validated_data == release_data
