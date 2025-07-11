"""API key authentication class for Django Ninja."""

from ninja.errors import HttpError
from ninja.security import APIKeyHeader

from apps.nest.models.api_key import APIKey


class ApiKeyAuth(APIKeyHeader):
    """Custom API key authentication class for Ninja."""

    param_name = "X-API-Key"

    def authenticate(self, request, key: str) -> APIKey:
        """Authenticate the API key from the request header.

        Args:
            request: The HTTP request object.
            key: The API key string from the request header.

        Returns:
            APIKey: The APIKey object if the key is valid, otherwise None.

        """
        if not key:
            raise HttpError(401, "Missing API key in 'X-API-Key' header")
        key_hash = APIKey.generate_hash_key(key)

        try:
            api_key = APIKey.objects.get(hash=key_hash)
            if api_key.is_valid():
                return api_key
        except APIKey.DoesNotExist as err:
            raise HttpError(401, "Invalid or expired API key") from err

        raise HttpError(401, "API key revoked or expired")
