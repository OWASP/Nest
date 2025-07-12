"""API key authentication class for Django Ninja."""

from ninja.errors import HttpError
from ninja.security import APIKeyHeader

from apps.nest.models.api_key import ApiKey


class ApiKeyAuth(APIKeyHeader):
    """Custom API key authentication class for Ninja."""

    param_name = "X-API-Key"

    def authenticate(self, request, key: str) -> ApiKey:
        """Authenticate the API key from the request header.

        Args:
            request: The HTTP request object.
            key: The API key string from the request header.

        Returns:
            APIKey: The APIKey object if the key is valid, otherwise None.

        """
        if not key:
            raise HttpError(401, "Missing API key in 'X-API-Key' header")

        try:
            api_key = ApiKey.objects.get(hash=ApiKey.generate_hash_key(key))
            if api_key.is_valid():
                return api_key
        except ApiKey.DoesNotExist as err:
            raise HttpError(401, "Invalid API key") from err

        raise HttpError(401, "Invalid API key")
