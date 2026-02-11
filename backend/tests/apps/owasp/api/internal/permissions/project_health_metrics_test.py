"""Test cases for HasDashboardAccess permission."""

from unittest.mock import Mock

import pytest

from apps.owasp.api.internal.permissions.project_health_metrics import HasDashboardAccess


class TestHasDashboardAccess:
    """Test cases for HasDashboardAccess permission class."""

    @pytest.fixture
    def permission(self):
        """Create permission instance."""
        return HasDashboardAccess()

    @pytest.fixture
    def mock_info_with_authenticated_staff(self):
        """Mock info with authenticated OWASP staff user."""
        info = Mock()
        info.context.request.user.is_authenticated = True
        info.context.request.user.github_user.is_owasp_staff = True
        return info

    @pytest.fixture
    def mock_info_with_authenticated_non_staff(self):
        """Mock info with authenticated non-staff user."""
        info = Mock()
        info.context.request.user.is_authenticated = True
        info.context.request.user.github_user.is_owasp_staff = False
        return info

    @pytest.fixture
    def mock_info_with_unauthenticated_user(self):
        """Mock info with unauthenticated user."""
        info = Mock()
        info.context.request.user.is_authenticated = False
        return info

    def test_permission_in_e2e_environment(self, permission, settings):
        """Test permission is granted in E2E environment."""
        settings.IS_E2E_ENVIRONMENT = True
        settings.IS_FUZZ_ENVIRONMENT = False
        settings.IS_STAGING_ENVIRONMENT = False

        info = Mock()
        result = permission.has_permission(source=None, info=info)

        assert result is True

    def test_permission_in_fuzz_environment(self, permission, settings):
        """Test permission is granted in Fuzz environment."""
        settings.IS_E2E_ENVIRONMENT = False
        settings.IS_FUZZ_ENVIRONMENT = True
        settings.IS_STAGING_ENVIRONMENT = False

        info = Mock()
        result = permission.has_permission(source=None, info=info)

        assert result is True

    def test_permission_in_staging_environment(self, permission, settings):
        """Test permission is granted in Staging environment."""
        settings.IS_E2E_ENVIRONMENT = False
        settings.IS_FUZZ_ENVIRONMENT = False
        settings.IS_STAGING_ENVIRONMENT = True

        info = Mock()
        result = permission.has_permission(source=None, info=info)

        assert result is True

    def test_permission_with_authenticated_staff(
        self, permission, settings, mock_info_with_authenticated_staff
    ):
        """Test permission is granted for authenticated OWASP staff."""
        settings.IS_E2E_ENVIRONMENT = False
        settings.IS_FUZZ_ENVIRONMENT = False
        settings.IS_STAGING_ENVIRONMENT = False

        result = permission.has_permission(
            source=None, info=mock_info_with_authenticated_staff
        )

        assert result is True

    def test_permission_with_authenticated_non_staff(
        self, permission, settings, mock_info_with_authenticated_non_staff
    ):
        """Test permission is denied for authenticated non-staff user."""
        settings.IS_E2E_ENVIRONMENT = False
        settings.IS_FUZZ_ENVIRONMENT = False
        settings.IS_STAGING_ENVIRONMENT = False

        result = permission.has_permission(
            source=None, info=mock_info_with_authenticated_non_staff
        )

        assert result is False

    def test_permission_with_unauthenticated_user(
        self, permission, settings, mock_info_with_unauthenticated_user
    ):
        """Test permission is denied for unauthenticated user."""
        settings.IS_E2E_ENVIRONMENT = False
        settings.IS_FUZZ_ENVIRONMENT = False
        settings.IS_STAGING_ENVIRONMENT = False

        result = permission.has_permission(
            source=None, info=mock_info_with_unauthenticated_user
        )

        assert result is False

    def test_permission_message(self, permission):
        """Test permission has correct message."""
        assert permission.message == "You must have dashboard access to access this resource."
