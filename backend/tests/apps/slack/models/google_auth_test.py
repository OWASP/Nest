"""Tests for GoogleAuth model."""

from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
from django.test import override_settings
from django.utils import timezone
from google_auth_oauthlib.flow import Flow

from apps.slack.models.google_auth import GoogleAuth
from apps.slack.models.member import Member


class TestGoogleAuthModel:
    """Test cases for GoogleAuth model."""

    @pytest.fixture(autouse=True)
    def setUp(self):
        """Set up test data."""
        self.member = Member(slack_user_id="U123456789", username="testuser")
        self.valid_token = "valid_access_token"  # noqa: S105
        self.valid_refresh_token = "valid_refresh_token"  # noqa: S105
        self.expired_time = timezone.now() - timedelta(hours=1)
        self.future_time = timezone.now() + timedelta(hours=1)

    def test_google_auth_creation(self):
        """Test GoogleAuth model creation."""
        auth = GoogleAuth(
            member=self.member,
            access_token=self.valid_token,
            refresh_token=self.valid_refresh_token,
            expires_at=self.future_time,
        )

        assert auth.member == self.member
        assert auth.access_token == self.valid_token
        assert auth.refresh_token == self.valid_refresh_token
        assert auth.expires_at == self.future_time

    def test_string_representation(self):
        """Test string representation of GoogleAuth."""
        auth = GoogleAuth(member=self.member, access_token=self.valid_token)

        expected = f"GoogleAuth(member={self.member})"
        assert str(auth) == expected

    def test_one_to_one_relationship(self):
        """Test one-to-one relationship with Member."""
        auth = GoogleAuth(member=self.member, access_token=self.valid_token)

        assert self.member.google_auth == auth
        assert auth.member == self.member

    def test_is_token_expired_with_future_expiry(self):
        """Test is_token_expired property with future expiry."""
        auth = GoogleAuth(
            member=self.member, access_token=self.valid_token, expires_at=self.future_time
        )

        assert not auth.is_token_expired

    def test_is_token_expired_with_past_expiry(self):
        """Test is_token_expired property with past expiry."""
        auth = GoogleAuth(
            member=self.member, access_token=self.valid_token, expires_at=self.expired_time
        )

        assert auth.is_token_expired

    def test_is_token_expired_with_none_expiry(self):
        """Test is_token_expired property with None expiry."""
        auth = GoogleAuth(member=self.member, access_token=self.valid_token, expires_at=None)

        assert auth.is_token_expired

    @override_settings(IS_GOOGLE_AUTH_ENABLED=False)
    def test_get_flow_when_disabled(self):
        """Test get_flow raises error when Google auth is disabled."""
        with pytest.raises(ValueError, match="Google OAuth client ID"):
            GoogleAuth.get_flow()

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    @override_settings(IS_GOOGLE_AUTH_ENABLED=True)
    @patch("apps.slack.models.google_auth.Flow.from_client_config")
    def test_get_flow_success(self, mock_flow):
        """Test successful get_flow creation."""
        mock_flow_instance = Mock(spec=Flow)
        mock_flow.return_value = mock_flow_instance

        result = GoogleAuth.get_flow()

        assert result == mock_flow_instance

    @override_settings(IS_GOOGLE_AUTH_ENABLED=False)
    def test_authenticate_when_disabled(self):
        """Test authenticate raises error when Google auth is disabled."""
        with pytest.raises(ValueError, match="Google OAuth client ID"):
            GoogleAuth.authenticate("http://auth.url", self.member)  # NOSONAR

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    @patch("apps.slack.models.google_auth.GoogleAuth.save")
    @patch("apps.slack.models.google_auth.GoogleAuth.objects.get_or_create")
    @patch("apps.slack.models.google_auth.GoogleAuth.get_flow")
    def test_authenticate_existing_valid_token(self, mock_get_flow, mock_get_or_create, mock_save):
        """Test authenticate with existing valid token."""
        # Create existing auth with valid token

        mock_get_flow.return_value = Mock(spec=Flow)
        mock_get_or_create.return_value = (
            GoogleAuth(
                member=self.member,
                access_token=self.valid_token,
                refresh_token=self.valid_refresh_token,
                expires_at=self.future_time,
            ),
            True,
        )
        result = GoogleAuth.authenticate("http://auth.url", self.member)  # NOSONAR

        assert result.access_token == self.valid_token
        assert result.refresh_token == self.valid_refresh_token
        assert result.expires_at == self.future_time
        mock_get_or_create.assert_called_once_with(member=self.member)
        mock_save.assert_not_called()

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    @patch("apps.slack.models.google_auth.GoogleAuth.refresh_access_token")
    @patch("apps.slack.models.google_auth.GoogleAuth.objects.get_or_create")
    def test_authenticate_existing_expired_token(self, mock_get_or_create, mock_refresh):
        """Test authenticate with existing expired token."""
        # Create existing auth with expired token
        existing_auth = GoogleAuth(
            member=self.member,
            access_token=self.valid_token,
            refresh_token=self.valid_refresh_token,
            expires_at=self.expired_time,
        )
        mock_get_or_create.return_value = (existing_auth, False)

        GoogleAuth.authenticate("http://auth.url", self.member)  # NOSONAR

        mock_refresh.assert_called_once_with(existing_auth)
        mock_get_or_create.assert_called_once_with(member=self.member)

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    @patch("apps.slack.models.google_auth.GoogleAuth.get_flow")
    @patch("apps.slack.models.google_auth.GoogleAuth.save")
    @patch("apps.slack.models.google_auth.GoogleAuth.objects.get_or_create")
    def test_authenticate_first_time(self, mock_get_or_create, mock_save, mock_get_flow):
        """Test authenticate for first time (no existing token)."""
        # Mock flow and credentials
        mock_credentials = Mock()
        mock_credentials.token = "new_access_token"  # noqa: S105 # NOSONAR
        mock_credentials.refresh_token = "new_refresh_token"  # noqa: S105
        mock_credentials.expiry = self.future_time

        mock_flow_instance = Mock()
        mock_flow_instance.credentials = mock_credentials
        mock_get_flow.return_value = mock_flow_instance
        mock_get_or_create.return_value = (
            GoogleAuth(
                member=self.member,
                access_token="",
                refresh_token="",
                expires_at=None,
            ),
            True,
        )

        result = GoogleAuth.authenticate("http://auth.url", self.member)  # NOSONAR

        assert result.access_token == "new_access_token"  # noqa: S105
        assert result.refresh_token == "new_refresh_token"  # noqa: S105
        assert result.expires_at == self.future_time
        mock_get_or_create.assert_called_once_with(member=self.member)

        mock_flow_instance.fetch_token.assert_called_once_with(
            authorization_response="http://auth.url",  # NOSONAR
        )
        mock_save.assert_called_once()

    @override_settings(IS_GOOGLE_AUTH_ENABLED=False)
    def test_refresh_access_token_when_disabled(self):
        """Test refresh_access_token raises error when Google auth is disabled."""
        auth = GoogleAuth(
            member=self.member,
            access_token=self.valid_token,
            refresh_token=self.valid_refresh_token,
        )

        with pytest.raises(ValueError, match="Google OAuth client ID"):
            GoogleAuth.refresh_access_token(auth)

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    @patch("apps.slack.models.google_auth.GoogleAuth.get_flow")
    @patch("apps.slack.models.google_auth.GoogleAuth.save")
    def test_refresh_access_token_success(self, mock_save, mock_get_flow):
        """Test successful refresh_access_token."""
        # Create auth with refresh token
        auth = GoogleAuth(
            member=self.member,
            access_token=self.valid_token,
            refresh_token=self.valid_refresh_token,
            expires_at=self.expired_time,
        )

        # Mock flow and new credentials
        mock_credentials = Mock()
        mock_credentials.token = "new_access_token"  # noqa: S105 # NOSONAR
        mock_credentials.refresh_token = "new_refresh_token"  # noqa: S105
        mock_credentials.expiry = self.future_time

        mock_flow_instance = Mock()
        mock_flow_instance.credentials = mock_credentials
        mock_get_flow.return_value = mock_flow_instance

        GoogleAuth.refresh_access_token(auth)

        assert auth.access_token == "new_access_token"  # noqa: S105
        assert auth.refresh_token == "new_refresh_token"  # noqa: S105
        assert auth.expires_at == self.future_time

        mock_flow_instance.fetch_token.assert_called_once_with(
            refresh_token=self.valid_refresh_token,
            client_id="test_client_id",
            client_secret="test_client_secret",  # noqa: S106
        )
        mock_save.assert_called_once()

    def test_verbose_names(self):
        """Test model field verbose names."""
        auth = GoogleAuth(member=self.member, access_token=self.valid_token)

        assert auth._meta.get_field("member").verbose_name == "Slack Member"
        assert auth._meta.get_field("access_token").verbose_name == "Access Token"
        assert auth._meta.get_field("refresh_token").verbose_name == "Refresh Token"
        assert auth._meta.get_field("expires_at").verbose_name == "Token Expiry"

    def test_refresh_token_blank_allowed(self):
        """Test that refresh_token can be blank."""
        auth = GoogleAuth(
            member=self.member,
            access_token=self.valid_token,
            refresh_token="",  # Blank is allowed
        )

        assert auth.refresh_token == ""

    def test_expires_at_null_allowed(self):
        """Test that expires_at can be null."""
        auth = GoogleAuth(
            member=self.member,
            access_token=self.valid_token,
            expires_at=None,  # Null is allowed
        )

        assert auth.expires_at is None


class TestGoogleAuthIntegration:
    """Integration tests for GoogleAuth model."""

    def test_full_authentication_flow(self):
        """Test complete authentication flow."""
        member = Member(slack_user_id="U123456789", username="testuser")

        # Test that we can create and use GoogleAuth
        with override_settings(
            IS_GOOGLE_AUTH_ENABLED=True,
            GOOGLE_AUTH_CLIENT_ID="integration_client_id",
            GOOGLE_AUTH_CLIENT_SECRET="integration_client_secret",  # noqa: S106
            GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
        ):
            # Test flow creation doesn't raise errors
            with patch("apps.slack.models.google_auth.Flow.from_client_config") as mock_flow:
                mock_flow.return_value = Mock(spec=Flow)
                flow = GoogleAuth.get_flow()
                assert flow is not None

            # Test authentication with valid token
            auth = GoogleAuth(
                member=member,
                access_token="integration_token",  # noqa: S106
                refresh_token="integration_refresh",  # noqa: S106
                expires_at=timezone.now() + timedelta(hours=1),
            )

            assert not auth.is_token_expired
            assert str(auth) == f"GoogleAuth(member={member})"
            assert member.google_auth == auth
