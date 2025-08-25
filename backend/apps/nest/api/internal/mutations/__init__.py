"""Nest app mutations."""

import strawberry

from .api_key import ApiKeyMutations
from .user import UserMutations


@strawberry.type
class NestMutations(ApiKeyMutations, UserMutations):
    """Nest mutations."""
