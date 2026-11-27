"""API key authentication class for Django Ninja."""

from http import HTTPStatus

from ninja.errors import HttpError
from ninja.security import APIKeyHeader

from apps.api.models.api_key import ApiKey as ApiKeyModel


class ApiKey(APIKeyHeader):
    """API key authentication."""

    param_name = "X-API-Key"

    def authenticate(self, request, key: str) -> ApiKeyModel:
        """Authenticate the API key from the request header.

        Args:
            request: The HTTP request object.
            key: The API key string from the request header.

        Returns:
            APIKey: The APIKey object if the key is valid, otherwise None.

        """
        error_message = f"Missing or invalid API key in '{self.param_name}' header"

        if not key:
            raise HttpError(HTTPStatus.UNAUTHORIZED, error_message)

        if api_key := ApiKeyModel.authenticate(raw_key=key):
            return api_key

        raise HttpError(HTTPStatus.UNAUTHORIZED, error_message)
