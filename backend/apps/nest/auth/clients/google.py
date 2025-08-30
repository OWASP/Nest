"""Google OAuth client."""

from django.conf import settings
from google_auth_oauthlib.flow import Flow


def get_google_auth_client() -> Flow:
    """Get a Google OAuth client."""
    return Flow.from_client_config(
        client_config={
            "web": {
                "auth_uri": settings.GOOGLE_AUTH_AUTH_URI,
                "client_id": settings.GOOGLE_AUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_AUTH_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_AUTH_REDIRECT_URI],
                "token_uri": settings.GOOGLE_AUTH_TOKEN_URI,
            }
        },
        scopes=settings.GOOGLE_AUTH_SCOPES,
    )
