"""Utilities for OWASP entity leadership checks."""

from django.contrib.contenttypes.models import ContentType

from apps.github.models.user import User as GithubUser
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project


def user_is_entity_leader(github_user: GithubUser, entity_model: type) -> bool:
    """Return True if the GitHub user is an active, reviewed leader of the entity type."""
    return EntityMember.objects.filter(
        member=github_user,
        entity_type=ContentType.objects.get_for_model(entity_model),
        role=EntityMember.Role.LEADER,
        is_active=True,
        is_reviewed=True,
    ).exists()


def user_is_project_leader(github_user: GithubUser) -> bool:
    """Return True if the GitHub user is an active, reviewed OWASP project leader."""
    return user_is_entity_leader(github_user, Project)
