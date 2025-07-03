"""Core User mutations."""

import strawberry

from .apikey import APIKeyMutations
from .user import UserMutations


@strawberry.type
class NestMutations(APIKeyMutations, UserMutations):
    """Nest mutations."""
