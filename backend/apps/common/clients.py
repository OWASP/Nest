"""Common API Clients."""

from django.conf import settings
from google_auth_oauthlib.flow import Flow


def get_google_auth_client():
    """Get a Google OAuth client."""
    return Flow.from_client_config(
        client_config={
            "web": {
                "client_id": settings.GOOGLE_AUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_AUTH_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_AUTH_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
    )
