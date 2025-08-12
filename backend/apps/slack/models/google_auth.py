"""Slack Google OAuth Authentication Model."""

from django.conf import settings
from django.db import models
from django.utils import timezone
from google_auth_oauthlib.flow import Flow

AUTH_ERROR_MESSAGE = (
    "Google OAuth client ID, secret, and redirect URI must be set in environment variables."
)


class GoogleAuth(models.Model):
    """Model to store Google OAuth tokens for Slack integration."""

    member = models.OneToOneField(
        "slack.Member",
        on_delete=models.CASCADE,
        related_name="google_auth",
        verbose_name="Slack Member",
    )
    access_token = models.BinaryField(
        verbose_name="Access Token",
        blank=True,
    )
    refresh_token = models.BinaryField(
        verbose_name="Refresh Token",
        blank=True,
    )
    expires_at = models.DateTimeField(
        verbose_name="Token Expiry",
        blank=True,
        null=True,
    )

    @staticmethod
    def get_flow():
        """Create a Google OAuth flow instance."""
        if not settings.IS_GOOGLE_AUTH_ENABLED:
            raise ValueError(AUTH_ERROR_MESSAGE)
        return Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": settings.GOOGLE_AUTH_CLIENT_ID,
                    "client_secret": settings.GOOGLE_AUTH_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_AUTH_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        )

    @staticmethod
    def authenticate(auth_url, member):
        """Authenticate a member and return a GoogleAuth instance."""
        if not settings.IS_GOOGLE_AUTH_ENABLED:
            raise ValueError(AUTH_ERROR_MESSAGE)
        auth = GoogleAuth.objects.get_or_create(member=member)[0]
        if auth.access_token and not auth.is_token_expired:
            return auth
        if auth.access_token:
            # If the access token is present but expired, refresh it
            GoogleAuth.refresh_access_token(auth)
            return auth
        # This is the first time authentication, so we need to fetch a new token
        flow = GoogleAuth.get_flow()
        flow.redirect_uri = settings.GOOGLE_AUTH_REDIRECT_URI
        flow.fetch_token(authorization_response=auth_url)
        auth.access_token = flow.credentials.token
        auth.refresh_token = flow.credentials.refresh_token
        auth.expires_at = flow.credentials.expiry
        auth.save()
        return auth

    @property
    def is_token_expired(self):
        """Check if the access token is expired."""
        return self.expires_at is None or self.expires_at <= timezone.now() + timezone.timedelta(
            seconds=60
        )

    @staticmethod
    def refresh_access_token(auth):
        """Refresh the access token using the refresh token."""
        if not settings.IS_GOOGLE_AUTH_ENABLED:
            raise ValueError(AUTH_ERROR_MESSAGE)
        refresh_error = "Google OAuth refresh token is not set or expired."
        if not auth.refresh_token:
            raise ValueError(refresh_error)

        flow = GoogleAuth.get_flow()
        flow.fetch_token(
            refresh_token=auth.refresh_token,
            client_id=settings.GOOGLE_AUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_AUTH_CLIENT_SECRET,
        )

        credentials = flow.credentials
        auth.access_token = credentials.token
        auth.refresh_token = credentials.refresh_token
        auth.expires_at = credentials.expiry
        auth.save()

    def __str__(self):
        """Return a string representation of the GoogleAuth instance."""
        return f"GoogleAuth(member={self.member})"
