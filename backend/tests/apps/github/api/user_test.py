from unittest.mock import MagicMock, patch

import pytest

from apps.github.api.user import UserSerializer, UserViewSet
from apps.github.models.user import User

http_status_ok = 200
http_status_not_found = 404


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
    @patch("apps.github.models.user.User.objects.filter")
    def test_user_serializer(self, mock_filter, user_data):
        mock_qs = MagicMock()

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
            ("johndoe", ["github", "microsoft"], True),
            ("github", ["github", "microsoft"], False),
            ("ghost", ["github", "microsoft"], False),
        ],
    )
    @patch("apps.github.models.organization.Organization.get_logins")
    def test_is_indexable(self, mock_get_logins, login, organization_logins, expected_result):
        mock_get_logins.return_value = organization_logins
        user = User(login=login)
        assert user.is_indexable == expected_result


class TestUserViewSet:
    @pytest.fixture
    def user_viewset(self):
        viewset = UserViewSet()
        viewset.request = None
        viewset.format_kwarg = None
        return viewset

    @patch("apps.github.models.user.User.objects.get")
    def test_get_user_by_login_success(self, mock_get, user_viewset):
        mock_user = MagicMock(spec=User)
        mock_user.login = "testuser"
        mock_user.name = "Test User"
        mock_get.return_value = mock_user

        request = MagicMock()
        user_viewset.request = request

        response = user_viewset.get_user_by_login(request, login="testuser")

        mock_get.assert_called_once_with(login="testuser")

        assert response.status_code == http_status_ok

    @patch("apps.github.models.user.User.objects.get")
    def test_get_user_by_login_not_found(self, mock_get, user_viewset):
        mock_get.side_effect = User.DoesNotExist

        request = MagicMock()
        user_viewset.request = request

        response = user_viewset.get_user_by_login(request, login="nonexistentuser")

        assert response.status_code == http_status_not_found
        assert response.data == {"detail": "User not found."}
