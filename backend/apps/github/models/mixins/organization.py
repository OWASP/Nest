"""GitHub organization mixins."""

from __future__ import annotations


class OrganizationIndexMixin:
    """Organization index mixin."""

    @property
    def is_indexable(self) -> bool:
        """Determine if the organization is indexable.

        Returns:
            bool: True if it's an OWASP-related organization with a name and login, False otherwise.
        """
        return bool(self.is_owasp_related_organization and self.name and self.login)

    @property
    def idx_avatar_url(self) -> str:
        """Return the avatar URL for indexing.

        Returns:
            str: The URL of the organization's avatar.
        """
        return self.avatar_url

    @property
    def idx_collaborators_count(self):
        """Return the collaborators count for indexing.

        This calculates the total number of unique collaborators across all repositories
        owned by this organization.

        Returns:
            int: The total count of unique collaborators.
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
        """Return the created at timestamp for indexing.

        Returns:
            float | None: The creation timestamp, or None if not available.
        """
        return self.created_at.timestamp() if self.created_at else None

    @property
    def idx_description(self) -> str:
        """Return the description for indexing.

        Returns:
            str: The organization's description.
        """
        return self.description or ""

    @property
    def idx_followers_count(self) -> int:
        """Return the followers count for indexing.

        Returns:
            int: The number of followers the organization has.
        """
        return self.followers_count

    @property
    def idx_location(self) -> str:
        """Return the location for indexing.

        Returns:
            str: The organization's location.
        """
        return self.location or ""

    @property
    def idx_login(self) -> str:
        """Return the login for indexing.

        Returns:
            str: The organization's login name.
        """
        return self.login

    @property
    def idx_name(self) -> str:
        """Return the name for indexing.

        Returns:
            str: The organization's name.
        """
        return self.name or ""

    @property
    def idx_public_repositories_count(self) -> int:
        """Return the public repositories count for indexing.

        Returns:
            int: The number of public repositories owned by the organization.
        """
        return self.public_repositories_count

    @property
    def idx_url(self) -> str:
        """Return the URL for indexing.

        Returns:
            str: The URL of the organization's GitHub profile.
        """
        return self.url
