"""API key authentication class for Django Ninja."""

from http import HTTPStatus

from ninja.errors import HttpError
from ninja.security import APIKeyHeader

from apps.api.models.api_key import ApiKey


class ApiKeyHeader(APIKeyHeader):
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
            raise HttpError(HTTPStatus.UNAUTHORIZED, "Missing API key in 'X-API-Key' header")

        if api_key := ApiKey.authenticate(raw_key=key):
            return api_key

        raise HttpError(HTTPStatus.UNAUTHORIZED, "Invalid API key")
