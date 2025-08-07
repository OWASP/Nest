"""Slack Google OAuth Authentication Model."""

import os

from django.db import models
from django.utils import timezone
from google_auth_oauthlib.flow import Flow


class GoogleSlackAuth(models.Model):
    """Model to store Google OAuth tokens for Slack integration."""

    user = models.OneToOneField(
        "slack.Member",
        on_delete=models.CASCADE,
        related_name="google_slack_auth",
        verbose_name="Slack Member",
    )
    access_token = models.CharField(
        max_length=255,
        verbose_name="Access Token",
    )
    refresh_token = models.CharField(
        max_length=255,
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
        return Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": os.getenv("GOOGLE_AUTH_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_AUTH_CLIENT_SECRET"),
                    "redirect_uris": [os.getenv("GOOGLE_AUTH_REDIRECT_URI")],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        )

    @staticmethod
    def authenticate(auth_url, user):
        """Authenticate a user and return a GoogleSlackAuth instance."""
        auth = GoogleSlackAuth.objects.get_or_create(user=user)[0]
        if auth.access_token and not auth.is_token_expired:
            return auth
        if auth.access_token:
            GoogleSlackAuth.refresh_access_token(auth)
            return auth
        flow = GoogleSlackAuth.get_flow()
        flow.redirect_uri = os.getenv("GOOGLE_AUTH_REDIRECT_URI")
        flow.fetch_token(authorization_response=auth_url)
        auth.access_token = flow.credentials.token
        auth.refresh_token = flow.credentials.refresh_token
        auth.expires_at = flow.credentials.expiry
        auth.save()
        return auth

    @property
    def is_token_expired(self):
        """Check if the access token is expired."""
        return self.expires_at is None or self.expires_at <= timezone.now()

    @staticmethod
    def refresh_access_token(auth):
        """Refresh the access token using the refresh token."""
        if not auth.refresh_token:
            raise ValueError("No refresh token available to refresh access token.")

        flow = GoogleSlackAuth.get_flow()
        flow.fetch_token(
            refresh_token=auth.refresh_token,
            client_id=os.getenv("GOOGLE_AUTH_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_AUTH_CLIENT_SECRET"),
        )

        credentials = flow.credentials
        auth.access_token = credentials.token
        auth.refresh_token = credentials.refresh_token
        auth.expires_at = credentials.expiry
        auth.save()

    def __str__(self):
        return f"GoogleSlackAuth(user={self.user})"
