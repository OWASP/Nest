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


class KmsClient:
    """AWS KMS Client."""

    def __init__(self):
        """Initialize the KMS client."""
        self.client = boto3.client(
            "kms",
            region_name=settings.AWS_REGION,
        )

    def decrypt(self, text: bytes) -> str:
        """Decrypt the ciphertext using KMS."""
        return self.client.decrypt(KeyId=settings.AWS_KMS_KEY_ID, CiphertextBlob=text)[
            "Plaintext"
        ].decode("utf-8")

    def encrypt(self, text: str) -> bytes:
        """Encrypt the plaintext using KMS."""
        return self.client.encrypt(KeyId=settings.AWS_KMS_KEY_ID, Plaintext=text.encode("utf-8"))[
            "CiphertextBlob"
        ]


kms_client = KmsClient()
