from unittest.mock import MagicMock, patch

import pytest

from apps.github.api.user import UserSerializer


@pytest.mark.parametrize(
    "user_data",
    [
        {
            "name": "John Doe",
            "login": "johndoe",
            "company": "GitHub",
            "location": "San Francisco",
            "created_at": "2024-12-30T00:00:00Z",
            "updated_at": "2024-12-30T00:00:00Z",
        },
        {
            "name": "Jane Smith",
            "login": "janesmith",
            "company": "Microsoft",
            "location": "Redmond",
            "created_at": "2024-12-29T00:00:00Z",
            "updated_at": "2024-12-30T00:00:00Z",
        },
    ],
)
@patch("apps.github.models.user.User.objects.filter")
def test_user_serializer(mock_filter, user_data):
    """Test the OrganizationSerializer with various organization data."""
    # Mock the queryset
    mock_qs = MagicMock()
    mock_qs.exists.return_value = False
    mock_filter.return_value = mock_qs

    serializer = UserSerializer(data=user_data)
    assert serializer.is_valid()
    validated_data = serializer.validated_data
    validated_data["created_at"] = validated_data["created_at"].isoformat().replace("+00:00", "Z")
    validated_data["updated_at"] = validated_data["updated_at"].isoformat().replace("+00:00", "Z")
    assert validated_data == user_data
