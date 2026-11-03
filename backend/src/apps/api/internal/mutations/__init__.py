"""API app mutations."""

import strawberry

from .api_key import ApiKeyMutations


@strawberry.type
class ApiMutations(ApiKeyMutations):
    """API mutations."""
