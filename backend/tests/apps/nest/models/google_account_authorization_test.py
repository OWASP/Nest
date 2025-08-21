"""Tests for GoogleAccountAuthorization model."""

from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone
from google_auth_oauthlib.flow import Flow

from apps.nest.models.google_account_authorization import GoogleAccountAuthorization
from apps.slack.models.member import Member


class TestGoogleAccountAuthorizationModel:
    """Test cases for GoogleAccountAuthorization model."""

    @pytest.fixture(autouse=True)
    def setUp(self):
        """Set up test data."""
        self.member = Member(slack_user_id="U123456789", username="testuser")
        self.valid_token = b"valid_token"
        self.valid_refresh_token = b"valid_refresh_token"
        self.expired_time = timezone.now() - timedelta(hours=1)
        self.future_time = timezone.now() + timedelta(hours=1)

    def test_member_google_credentials_creation(self):
        """Test GoogleAccountAuthorization model creation."""
        auth = GoogleAccountAuthorization(
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
        """Test string representation of GoogleAccountAuthorization."""
        auth = GoogleAccountAuthorization(member=self.member, access_token=self.valid_token)

        expected = f"GoogleAccountAuthorization(member={self.member})"
        assert str(auth) == expected

    def test_one_to_one_relationship(self):
        """Test one-to-one relationship with Member."""
        auth = GoogleAccountAuthorization(member=self.member, access_token=self.valid_token)

        assert self.member.google_account_authorization == auth
        assert auth.member == self.member

    def test_is_token_expired_with_future_expiry(self):
        """Test is_token_expired property with future expiry."""
        auth = GoogleAccountAuthorization(
            member=self.member, access_token=self.valid_token, expires_at=self.future_time
        )

        assert not auth.is_token_expired

    def test_is_token_expired_with_past_expiry(self):
        """Test is_token_expired property with past expiry."""
        auth = GoogleAccountAuthorization(
            member=self.member, access_token=self.valid_token, expires_at=self.expired_time
        )

        assert auth.is_token_expired

    def test_is_token_expired_with_none_expiry(self):
        """Test is_token_expired property with None expiry."""
        auth = GoogleAccountAuthorization(
            member=self.member, access_token=self.valid_token, expires_at=None
        )

        assert auth.is_token_expired

    @override_settings(IS_GOOGLE_AUTH_ENABLED=False)
    def test_get_flow_when_disabled(self):
        """Test get_flow raises error when Google auth is disabled."""
        with pytest.raises(ValueError, match="Google OAuth client ID"):
            GoogleAccountAuthorization.get_flow()

    @override_settings(IS_GOOGLE_AUTH_ENABLED=False)
    def test_authenticate_when_google_auth_disabled(self):
        """Test authenticate raises error when Google auth is disabled."""
        with pytest.raises(ValueError, match="Google OAuth client ID"):
            GoogleAccountAuthorization.authenticate(self.member)

    @override_settings(IS_AWS_KMS_ENABLED=False, IS_GOOGLE_AUTH_ENABLED=True)
    def test_authenticate_when_aws_kms_disabled(self):
        """Test authenticate raises error when AWS KMS is disabled."""
        with pytest.raises(ValueError, match="AWS KMS is not enabled"):
            GoogleAccountAuthorization.authenticate(self.member)

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        IS_AWS_KMS_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.save")
    @patch(
        "apps.nest.models.google_account_authorization.GoogleAccountAuthorization.objects.get_or_create"
    )
    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.get_flow")
    def test_authenticate_existing_valid_token(self, mock_get_flow, mock_get_or_create, mock_save):
        """Test authenticate with existing valid token."""
        # Create existing auth with valid token

        mock_get_flow.return_value = Mock(spec=Flow)
        mock_get_or_create.return_value = (
            GoogleAccountAuthorization(
                member=self.member,
                access_token=self.valid_token,
                refresh_token=self.valid_refresh_token,
                expires_at=self.future_time,
            ),
            True,
        )
        result = GoogleAccountAuthorization.authenticate(self.member)

        assert result.access_token == self.valid_token
        assert result.refresh_token == self.valid_refresh_token
        assert result.expires_at == self.future_time
        mock_get_or_create.assert_called_once_with(member=self.member)
        mock_save.assert_not_called()

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        IS_AWS_KMS_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    @patch(
        "apps.nest.models.google_account_authorization.GoogleAccountAuthorization.refresh_access_token"
    )
    @patch(
        "apps.nest.models.google_account_authorization.GoogleAccountAuthorization.objects.get_or_create"
    )
    def test_authenticate_existing_expired_token(self, mock_get_or_create, mock_refresh):
        """Test authenticate with existing expired token."""
        # Create existing auth with expired token
        existing_auth = GoogleAccountAuthorization(
            member=self.member,
            access_token=self.valid_token,
            refresh_token=self.valid_refresh_token,
            expires_at=self.expired_time,
        )
        mock_get_or_create.return_value = (existing_auth, False)

        GoogleAccountAuthorization.authenticate(self.member)

        mock_refresh.assert_called_once_with(existing_auth)
        mock_get_or_create.assert_called_once_with(member=self.member)

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        IS_AWS_KMS_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.get_flow")
    @patch(
        "apps.nest.models.google_account_authorization.GoogleAccountAuthorization.objects.get_or_create"
    )
    @patch("apps.nest.models.google_account_authorization.TimestampSigner")
    def test_authenticate_first_time(
        self, mock_timestamp_signer, mock_get_or_create, mock_get_flow
    ):
        """Test authenticate for first time (no existing token)."""
        # Mock flow and credentials
        mock_flow_instance = Mock()
        mock_get_flow.return_value = mock_flow_instance
        mock_get_or_create.return_value = (
            GoogleAccountAuthorization(
                member=self.member,
                access_token=None,
                refresh_token=None,
                expires_at=None,
            ),
            True,
        )
        mock_timestamp_signer.return_value.sign.return_value = "test_state"
        GoogleAccountAuthorization.authenticate(self.member)

        mock_get_or_create.assert_called_once_with(member=self.member)

        mock_flow_instance.authorization_url.assert_called_once_with(
            access_type="offline",
            prompt="consent",
            state="test_state",
        )

    @override_settings(IS_GOOGLE_AUTH_ENABLED=False)
    def test_refresh_access_token_when_google_auth_disabled(self):
        """Test refresh_access_token raises error when Google auth is disabled."""
        auth = GoogleAccountAuthorization(
            member=self.member,
            access_token=self.valid_token,
            refresh_token=self.valid_refresh_token,
        )

        with pytest.raises(ValueError, match="Google OAuth client ID"):
            GoogleAccountAuthorization.refresh_access_token(auth)

    @override_settings(IS_GOOGLE_AUTH_ENABLED=True, IS_AWS_KMS_ENABLED=False)
    def test_refresh_access_token_when_aws_kms_disabled(self):
        """Test refresh_access_token raises error when AWS KMS is disabled."""
        auth = GoogleAccountAuthorization(
            member=self.member,
            access_token=self.valid_token,
            refresh_token=self.valid_refresh_token,
        )

        with pytest.raises(ValueError, match="AWS KMS is not enabled."):
            GoogleAccountAuthorization.refresh_access_token(auth)

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        IS_AWS_KMS_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    @patch("apps.nest.models.google_account_authorization.Credentials")
    @patch("apps.nest.models.google_account_authorization.Request")
    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.save")
    def test_refresh_access_token_success(self, mock_save, mock_request, mock_credentials):
        """Test successful refresh_access_token."""
        # Create auth with refresh token
        auth = GoogleAccountAuthorization(
            member=self.member,
            access_token=self.valid_token,
            refresh_token=self.valid_refresh_token,
            expires_at=self.expired_time,
        )

        # Mock flow and new credentials
        mock_credentials_instance = Mock()
        mock_credentials_instance.token = b"token"  # NOSONAR
        mock_credentials_instance.refresh_token = b"refresh_token"
        mock_credentials_instance.expiry = self.future_time

        mock_credentials.return_value = mock_credentials_instance

        GoogleAccountAuthorization.refresh_access_token(auth)

        assert auth.access_token == b"token"
        assert auth.refresh_token == b"refresh_token"
        assert auth.expires_at == self.future_time

        mock_credentials.assert_called_once_with(
            token=self.valid_token,
            refresh_token=self.valid_refresh_token,
            token_uri=settings.GOOGLE_AUTH_TOKEN_URI,
            client_id=settings.GOOGLE_AUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_AUTH_CLIENT_SECRET,
        )
        mock_credentials_instance.refresh.assert_called_once_with(mock_request.return_value)
        mock_save.assert_called_once()

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        IS_AWS_KMS_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    def test_refresh_token_not_found(self):
        """Test refresh_access_token raises error when no refresh token is present."""
        auth = GoogleAccountAuthorization(
            member=self.member,
            access_token=self.valid_token,
            refresh_token=None,
        )

        with pytest.raises(
            ValidationError, match="Google OAuth refresh token is not set or expired."
        ):
            GoogleAccountAuthorization.refresh_access_token(auth)

    def test_verbose_names(self):
        """Test model field verbose names."""
        auth = GoogleAccountAuthorization(member=self.member, access_token=self.valid_token)

        assert auth._meta.get_field("member").verbose_name == "Slack Member"
        assert auth._meta.get_field("access_token").verbose_name == "Access Token"
        assert auth._meta.get_field("refresh_token").verbose_name == "Refresh Token"
        assert auth._meta.get_field("expires_at").verbose_name == "Token Expiry"

    @override_settings(IS_GOOGLE_AUTH_ENABLED=False)
    def test_authenticate_callback_member_google_credentials_disabled(self):
        """Test authenticate_callback raises error when Google auth is disabled."""
        with pytest.raises(ValueError, match="Google OAuth client ID"):
            GoogleAccountAuthorization.authenticate_callback(auth_response={})

    @override_settings(IS_AWS_KMS_ENABLED=False, IS_GOOGLE_AUTH_ENABLED=True)
    def test_authenticate_callback_kms_disabled(self):
        """Test authenticate_callback raises error when AWS KMS is disabled."""
        with pytest.raises(ValueError, match="AWS KMS is not enabled"):
            GoogleAccountAuthorization.authenticate_callback(auth_response={})

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        IS_AWS_KMS_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.get_flow")
    @patch(
        "apps.nest.models.google_account_authorization.GoogleAccountAuthorization.objects.get_or_create"
    )
    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.save")
    @patch("apps.nest.models.google_account_authorization.Member.objects.get")
    @patch("apps.nest.models.google_account_authorization.urlparse")
    @patch("apps.nest.models.google_account_authorization.parse_qs")
    @patch("apps.nest.models.google_account_authorization.TimestampSigner")
    def test_authenticate_callback_success(
        self,
        mock_timestamp_signer,
        mock_parse_qs,
        mock_urlparse,
        mock_member_get,
        mock_save,
        mock_get_or_create,
        mock_get_flow,
    ):
        """Test successful authenticate_callback."""
        mock_credentials = Mock()
        mock_credentials.token = b"token"  # NOSONAR
        mock_credentials.refresh_token = b"refresh_token"
        mock_credentials.expiry = self.future_time

        mock_flow_instance = Mock(spec=Flow)
        mock_flow_instance.credentials = mock_credentials
        mock_member_get.return_value = self.member
        mock_get_flow.return_value = mock_flow_instance
        mock_get_or_create.return_value = (GoogleAccountAuthorization(member=self.member), False)
        mock_parse_qs.return_value = {"state": ["test_state"]}
        mock_timestamp_signer.return_value.unsign.return_value = self.member.slack_user_id

        result = GoogleAccountAuthorization.authenticate_callback({})

        assert result.access_token == b"token"
        assert result.refresh_token == b"refresh_token"
        assert result.expires_at == self.future_time
        mock_get_or_create.assert_called_once_with(member=self.member)
        mock_save.assert_called_once()
        mock_flow_instance.fetch_token.assert_called_once_with(authorization_response={})

    @override_settings(
        IS_GOOGLE_AUTH_ENABLED=True,
        IS_AWS_KMS_ENABLED=True,
        GOOGLE_AUTH_CLIENT_ID="test_client_id",
        GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
        GOOGLE_AUTH_REDIRECT_URI="http://localhost:8000/callback",
    )
    @patch("apps.slack.models.member.Member.objects.get")
    @patch("apps.nest.models.google_account_authorization.urlparse")
    @patch("apps.nest.models.google_account_authorization.parse_qs")
    @patch("apps.nest.models.google_account_authorization.TimestampSigner")
    def test_authenticate_callback_member_not_found(
        self, mock_timestamp_signer, mock_parse_qs, mock_urlparse, mock_member_get
    ):
        """Test authenticate_callback raises error when member is not found."""
        mock_member_get.side_effect = Member.DoesNotExist
        mock_urlparse.return_value = Mock()
        mock_parse_qs.return_value.get.return_value = ["test_state"]
        mock_timestamp_signer.return_value.unsign.return_value = "4"
        with pytest.raises(ValidationError, match="Member with Slack ID 4 does not exist."):
            GoogleAccountAuthorization.authenticate_callback(auth_response={})
