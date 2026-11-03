"""Nest app mutations."""

import strawberry

from .user import UserMutations


@strawberry.type
class NestMutations(UserMutations):
    """Nest mutations."""
