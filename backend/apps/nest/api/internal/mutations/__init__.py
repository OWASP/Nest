"""Nest app mutations."""

import strawberry

from .api_key import ApiKeyMutations
from .badge import BadgeMutations
from .user import UserMutations


@strawberry.type
class NestMutations(ApiKeyMutations, BadgeMutations, UserMutations):
    """Nest mutations."""
