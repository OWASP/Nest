from unittest.mock import MagicMock, patch

import pytest

from apps.github.api.user import UserSerializer
from apps.github.models.user import User


class TestUserSerializer:
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
                "login": "jane-smith",
                "company": "Microsoft",
                "location": "Redmond",
                "created_at": "2024-12-29T00:00:00Z",
                "updated_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    # Ensures that test runs without actual database access by simulating behavior of a queryset.
    @patch("apps.github.models.user.User.objects.filter")
    def test_user_serializer(self, mock_filter, user_data):
        mock_qs = MagicMock()
        # To mimic a queryset where no matching objects are found.
        mock_qs.exists.return_value = False
        mock_filter.return_value = mock_qs

        serializer = UserSerializer(data=user_data)
        assert serializer.is_valid()
        validated_data = serializer.validated_data

        validated_data["created_at"] = (
            validated_data["created_at"].isoformat().replace("+00:00", "Z")
        )
        validated_data["updated_at"] = (
            validated_data["updated_at"].isoformat().replace("+00:00", "Z")
        )
        assert validated_data == user_data

    @pytest.mark.parametrize(
        ("login", "organization_logins", "expected_result"),
        [
            ("johndoe", ["github", "microsoft"], True),  # Normal user
            ("github", ["github", "microsoft"], False),  # Organization login
            ("ghost", ["github", "microsoft"], False),  # Special 'ghost' user
        ],
    )
    @patch("apps.github.models.organization.Organization.get_logins")
    def test_is_indexable(self, mock_get_logins, login, organization_logins, expected_result):
        mock_get_logins.return_value = organization_logins
        user = User(login=login)
        assert user.is_indexable == expected_result
