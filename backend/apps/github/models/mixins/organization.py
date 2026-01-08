"""GitHub organization mixins."""

from __future__ import annotations


class OrganizationIndexMixin:
    """Organization index mixin."""

    @property
    def is_indexable(self) -> bool:
        """Determine if the organization should be indexed.

        Returns:
            bool: True if the organization meets indexing criteria, False otherwise.

        """
        return bool(self.is_owasp_related_organization and self.name and self.login)

    @property
    def idx_avatar_url(self) -> str:
        """Return avatar URL for indexing.

        Returns:
            str: The URL of the organization's avatar.

        """
        return self.avatar_url

    @property
    def idx_collaborators_count(self):
        """Return collaborators count for indexing.

        This calculates the total number of unique collaborators across all repositories
        owned by this organization.

        Returns:
            int: The number of unique collaborators.

        """
        from apps.github.models.repository import Repository
        from apps.github.models.repository_contributor import RepositoryContributor

        repositories = Repository.objects.filter(organization=self)

        if repositories.exists():
            return (
                RepositoryContributor.objects.filter(repository__in=repositories)
                .values("user")
                .distinct()
                .count()
            )

        return self.collaborators_count

    @property
    def idx_created_at(self) -> float | None:
        """Return created at timestamp for indexing.

        Returns:
            float | None: The organization creation timestamp, or None.

        """
        return self.created_at.timestamp() if self.created_at else None

    @property
    def idx_description(self) -> str:
        """Return description for indexing.

        Returns:
            str: The description of the organization.

        """
        return self.description or ""

    @property
    def idx_followers_count(self) -> int:
        """Return followers count for indexing.

        Returns:
            int: The number of followers the organization has.

        """
        return self.followers_count

    @property
    def idx_location(self) -> str:
        """Return location for indexing.

        Returns:
            str: The location of the organization.

        """
        return self.location or ""

    @property
    def idx_login(self) -> str:
        """Return login for indexing.

        Returns:
            str: The login name of the organization.

        """
        return self.login

    @property
    def idx_name(self) -> str:
        """Return name for indexing.

        Returns:
            str: The display name of the organization.

        """
        return self.name or ""

    @property
    def idx_public_repositories_count(self) -> int:
        """Return public repositories count for indexing.

        Returns:
            int: The number of public repositories.

        """
        return self.public_repositories_count

    @property
    def idx_url(self) -> str:
        """Return URL for indexing.

        Returns:
            str: The URL of the organization's GitHub page.

        """
        return self.url
