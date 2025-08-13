"""Slack Google OAuth Authentication Model."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.common.clients import get_google_auth_client
from apps.slack.models.member import Member

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
    access_token = models.BinaryField(verbose_name="Access Token", null=True)
    refresh_token = models.BinaryField(verbose_name="Refresh Token", null=True)
    expires_at = models.DateTimeField(
        verbose_name="Token Expiry",
        null=True,
    )

    @staticmethod
    def authenticate(member):
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
        # If no access token is present, redirect to Google OAuth
        flow = GoogleAuth.get_flow()
        flow.redirect_uri = settings.GOOGLE_AUTH_REDIRECT_URI
        state = member.slack_user_id
        return flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=state,
        )

    @staticmethod
    def authenticate_callback(auth_response, member_id):
        """Authenticate a member and return a GoogleAuth instance."""
        if not settings.IS_GOOGLE_AUTH_ENABLED:
            raise ValueError(AUTH_ERROR_MESSAGE)

        member = None
        try:
            member = Member.objects.get(slack_user_id=member_id)
        except Member.DoesNotExist as e:
            error_message = f"Member with Slack ID {member_id} does not exist."
            raise ValidationError(error_message) from e

        auth = GoogleAuth.objects.get_or_create(member=member)[0]
        # This is the first time authentication, so we need to fetch a new token
        flow = GoogleAuth.get_flow()
        flow.redirect_uri = settings.GOOGLE_AUTH_REDIRECT_URI
        flow.fetch_token(authorization_response=auth_response)
        auth.access_token = flow.credentials.token
        auth.refresh_token = flow.credentials.refresh_token
        expires_at = flow.credentials.expiry
        if expires_at and timezone.is_naive(expires_at):
            expires_at = timezone.make_aware(expires_at)
        auth.expires_at = expires_at
        auth.save()
        return auth

    @staticmethod
    def get_flow():
        """Create a Google OAuth flow instance."""
        if not settings.IS_GOOGLE_AUTH_ENABLED:
            raise ValueError(AUTH_ERROR_MESSAGE)
        return get_google_auth_client()

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
            raise ValidationError(refresh_error)

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
