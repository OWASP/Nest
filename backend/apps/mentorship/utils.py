"""Utility functions for the mentorship app."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import strawberry

    from apps.mentorship.models.program import Program


def has_program_access(info: strawberry.Info, program: Program) -> bool:
    """Check if the current user has admin or mentor access to a program.

    Returns True if the user is authenticated and is either an admin or
    a mentor of the given program, False otherwise.
    """
    user = info.context.request.user
    if not user.is_authenticated:
        return False

    is_admin = program.admins.filter(nest_user=user).exists()
    if is_admin:
        return True

    if user.github_user:
        is_mentor = program.modules.filter(mentors__github_user=user.github_user).exists()
        if is_mentor:
            return True

    return False


def normalize_name(name):
    """Normalize a string by stripping whitespace and converting to lowercase."""
    return (name or "").strip().casefold()
