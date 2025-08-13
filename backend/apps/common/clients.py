"""Common API Clients."""

import boto3
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
                "auth_uri": settings.GOOGLE_AUTH_AUTH_URI,
                "token_uri": settings.GOOGLE_AUTH_TOKEN_URI,
            }
        },
        scopes=settings.GOOGLE_AUTH_SCOPES,
    )

kms_client = boto3.client(
    "kms",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)
