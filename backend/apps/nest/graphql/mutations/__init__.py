"""Core User mutations."""

import strawberry

from .api_key import APIKeyMutations
from .user import UserMutations


@strawberry.type
class NestMutations(APIKeyMutations, UserMutations):
    """Nest mutations."""
