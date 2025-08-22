"""Nest Google Account Authorization Model."""

import logging
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.db import models
from django.utils import timezone
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from apps.common.model_fields import KmsEncryptedField
from apps.nest.auth.clients.google import get_google_auth_client
from apps.slack.models.member import Member

logger = logging.getLogger(__name__)

AUTH_ERROR_MESSAGE = (
    "Google OAuth client ID, secret, and redirect URI must be set in environment variables."
)
KMS_ERROR_MESSAGE = "AWS KMS is not enabled."


class GoogleAccountAuthorization(models.Model):
    """Model to store Google OAuth tokens for Slack integration."""

    class Meta:
        db_table = "nest_google_account_authorizations"
        verbose_name_plural = "Google Accounts Authorizations"

    member = models.OneToOneField(
        "slack.Member",
        on_delete=models.CASCADE,
        related_name="google_account_authorization",
        verbose_name="Slack Member",
        null=True,
    )
    access_token = KmsEncryptedField(verbose_name="Access Token")
    refresh_token = KmsEncryptedField(verbose_name="Refresh Token")
    expires_at = models.DateTimeField(verbose_name="Token Expiry")
    scope = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )

    @staticmethod
    def authorize(slack_user_id: str):
        """Authorize a member.

        Returns:
            - GoogleAccountAuthorization instance if a valid/refreshable token exists, or
            - (authorization_url, state) tuple to complete the OAuth flow.

        """
        if not settings.IS_GOOGLE_AUTH_ENABLED:
            raise ValueError(AUTH_ERROR_MESSAGE)
        if not settings.IS_AWS_KMS_ENABLED:
            raise ValueError(KMS_ERROR_MESSAGE)
        try:
            member = Member.objects.get(slack_user_id=slack_user_id)
        except Member.DoesNotExist as e:
            error_message = f"Member with Slack ID {slack_user_id} does not exist."
            logger.exception(error_message)
            raise ValidationError(error_message) from e
        if GoogleAccountAuthorization.objects.filter(member=member).exists():
            auth = GoogleAccountAuthorization.objects.get(member=member)
            if not auth.is_token_expired:
                return auth
            try:
                GoogleAccountAuthorization.refresh_access_token(auth)
            except ValidationError:
                pass
            else:
                return auth
        flow = GoogleAccountAuthorization.get_flow()
        flow.redirect_uri = settings.GOOGLE_AUTH_REDIRECT_URI
        return flow.authorization_url(
            access_type="offline",
            prompt="consent",
            state=TimestampSigner(salt="google_auth").sign(member.slack_user_id),
        )

    @staticmethod
    def authorize_callback(auth_response):
        """Authorize a member and return a GoogleAccountAuthorization instance."""
        if not settings.IS_GOOGLE_AUTH_ENABLED:
            logger.exception(AUTH_ERROR_MESSAGE)
            raise ValueError(AUTH_ERROR_MESSAGE)

        if not settings.IS_AWS_KMS_ENABLED:
            logger.exception(KMS_ERROR_MESSAGE)
            raise ValueError(KMS_ERROR_MESSAGE)
        parsed_url = urlparse(auth_response)
        state = parse_qs(parsed_url.query).get("state", [None])[0]
        if not state:
            error_message = "State parameter is missing in the authentication response."
            raise ValidationError(error_message)

        try:
            member_id = TimestampSigner(salt="google_auth").unsign(state, max_age=3600)
        except (BadSignature, SignatureExpired) as e:
            error_message = f"Invalid state parameter: {state}"
            logger.exception(error_message)
            raise ValidationError(error_message) from e

        try:
            member = Member.objects.get(slack_user_id=member_id)
        except Member.DoesNotExist as e:
            error_message = f"Member with Slack ID {member_id} does not exist."
            logger.exception(error_message)
            raise ValidationError(error_message) from e
        # This is the first time authorization, so we need to fetch a new token
        flow = GoogleAccountAuthorization.get_flow()
        flow.redirect_uri = settings.GOOGLE_AUTH_REDIRECT_URI
        flow.fetch_token(authorization_response=auth_response)

        expires_at = flow.credentials.expiry
        if expires_at and timezone.is_naive(expires_at):
            expires_at = timezone.make_aware(expires_at)

        auth, _ = GoogleAccountAuthorization.objects.get_or_create(
            member=member,
            defaults={
                "access_token": flow.credentials.token,
                "refresh_token": flow.credentials.refresh_token,
                "expires_at": expires_at,
                "scope": settings.GOOGLE_AUTH_SCOPES,
            },
        )
        auth.access_token = flow.credentials.token
        if flow.credentials.refresh_token:
            auth.refresh_token = flow.credentials.refresh_token
        auth.expires_at = expires_at
        auth.scope = settings.GOOGLE_AUTH_SCOPES
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
        if not settings.IS_AWS_KMS_ENABLED:
            raise ValueError(KMS_ERROR_MESSAGE)
        if not auth.refresh_token:
            refresh_error = "Google OAuth refresh token is not set or expired."
            raise ValidationError(refresh_error)
        credentials = Credentials(
            token=auth.access_token,
            refresh_token=auth.refresh_token,
            token_uri=settings.GOOGLE_AUTH_TOKEN_URI,
            client_id=settings.GOOGLE_AUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_AUTH_CLIENT_SECRET,
        )
        try:
            credentials.refresh(Request())
        except RefreshError as e:
            error_message = "Error refreshing Google OAuth token"
            logger.exception(error_message)
            raise ValidationError(error_message) from e
        auth.access_token = credentials.token
        expires_at = credentials.expiry
        if expires_at and timezone.is_naive(expires_at):
            expires_at = timezone.make_aware(expires_at)
        if credentials.refresh_token:
            auth.refresh_token = credentials.refresh_token
        auth.expires_at = expires_at
        auth.save()

    def __str__(self):
        """Return a string representation of the GoogleAccountAuthorization instance."""
        return f"GoogleAccountAuthorization(member={self.member})"
