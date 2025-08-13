"""GitHub app common module."""

from __future__ import annotations

import logging

from apps.github.models.organization import Organization
from apps.github.models.repository import Repository
from apps.github.models.user import User
from apps.github.utils import check_owasp_site_repository

logger: logging.Logger = logging.getLogger(__name__)


def sync_repository(
    gh_repository, organization=None, user=None
) -> tuple[Organization, Repository]:
    """Sync GitHub repository data.

    Args:
        gh_repository (github.Repository.Repository): The GitHub repository object.
        organization (Organization, optional): The organization instance.
        user (User, optional): The user instance.

    Returns:
        tuple: A tuple containing the updated organization and repository instances.

    """
    entity_key = gh_repository.name.lower()
    is_owasp_site_repository = check_owasp_site_repository(entity_key)

    # GitHub repository organization.
    if organization is None:
        gh_organization = gh_repository.organization
        if gh_organization is not None:
            organization = Organization.update_data(gh_organization)

    # GitHub repository owner.
    if user is None:
        user = User.update_data(gh_repository.owner)

    # GitHub repository.
    commits = gh_repository.get_commits()
    contributors = gh_repository.get_contributors()
    languages = None if is_owasp_site_repository else gh_repository.get_languages()

    repository = Repository.update_data(
        gh_repository,
        commits=commits,
        contributors=contributors,
        languages=languages,
        organization=organization,
        user=user,
    )

    # Process repository content if not archived
    if not repository.is_archived:
        repository.sync_milestones(gh_repository)
        repository.sync_issues(gh_repository)
        repository.sync_pull_requests(gh_repository)

    repository.sync_releases(gh_repository, is_owasp_site_repository)
    repository.sync_contributors(gh_repository)

    return organization, repository
