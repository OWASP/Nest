"""Test cases for google sign in handler."""

from unittest.mock import Mock, patch

from apps.slack.blocks import markdown
from apps.slack.common.handlers.google_sign_in import get_blocks


class TestGoogleSignInHandler:
    """Test cases for GoogleSignInHandler."""

    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.authorize")
    def test_handle_google_sign_in_when_not_authorized(self, mock_auth):
        """Test handle_google_sign_in when not authorized."""
        mock_auth.return_value = ("test_url", "test_state")
        blocks = get_blocks("test_slack_user_id")
        mock_auth.assert_called_once_with("test_slack_user_id")
        assert blocks == [
            markdown("Please sign in to Google: <test_url|Click here>"),
        ]

    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.authorize")
    def test_handle_google_sign_in_when_authorized(self, mock_auth):
        """Test handle_google_sign_in when authorized."""
        mock_auth.return_value = Mock()
        blocks = get_blocks("test_slack_user_id")
        mock_auth.assert_called_once_with("test_slack_user_id")
        assert blocks == [markdown("✅ You are already signed in to Google.")]
