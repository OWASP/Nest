"""Test cases for google client."""

from unittest.mock import Mock, patch

from django.test import override_settings

from apps.nest.auth.clients.google import get_google_auth_client


@override_settings(
    IS_GOOGLE_AUTH_ENABLED=True,
    GOOGLE_AUTH_CLIENT_ID="test_client_id",
    GOOGLE_AUTH_CLIENT_SECRET="test_client_secret",  # noqa: S106
    GOOGLE_AUTH_REDIRECT_URI="test_redirect_uri",
)
@patch("apps.nest.auth.clients.google.Flow.from_client_config")
def test_google_auth_client(mock_from_client_config):
    """Test getting the Google OAuth client."""
    mock_from_client_config.return_value = Mock()
    client = get_google_auth_client()
    assert client is not None, "Google OAuth client should not be None."
    mock_from_client_config.assert_called_once_with(
        client_config={
            "web": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "redirect_uris": ["test_redirect_uri"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
    )
