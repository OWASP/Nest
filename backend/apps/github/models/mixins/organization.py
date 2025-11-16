"""GitHub organization mixins for index-related functionality."""

from __future__ import annotations


class OrganizationIndexMixin:
    """Organization index mixin providing properties for search indexing."""

    @property
    def is_indexable(self) -> bool:
        """
        Indicates if the organization should be indexed.

        Returns True if the organization is OWASP-related, has a name, and has a login.
        Returns False otherwise.

        Purpose: Determines whether this organization should appear in search indexes.
        """
        return bool(self.is_owasp_related_organization and self.name and self.login)

    @property
    def idx_avatar_url(self) -> str:
        """
        Returns the avatar URL of the organization.

        Purpose: Provides the organization's avatar for display in search indexes.
        """
        return self.avatar_url

    @property
    def idx_collaborators_count(self):
        """
        Returns the total number of unique collaborators across all repositories
        owned by this organization.

        Purpose: Used for indexing to provide insights into the organization's activity
        and reach within repositories.
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
        """
        Returns the creation timestamp of the organization.

        Purpose: Used for sorting or filtering organizations by creation date in search indexes.
        """
        return self.created_at.timestamp() if self.created_at else None

    @property
    def idx_description(self) -> str:
        """
        Returns the description of the organization.

        Purpose: Provides searchable descriptive content for indexing.
        """
        return self.description or ""

    @property
    def idx_followers_count(self) -> int:
        """
        Returns the followers count of the organization.

        Purpose: Provides insight into the organization's popularity for search ranking.
        """
        return self.followers_count

    @property
    def idx_location(self) -> str:
        """
        Returns the location of the organization.

        Purpose: Used for geographic filtering or search indexing.
        """
        return self.location or ""

    @property
    def idx_login(self) -> str:
        """
        Returns the login (username) of the organization.

        Purpose: Used as a unique key for indexing and search operations.
        """
        return self.login

    @property
    def idx_name(self) -> str:
        """
        Returns the name of the organization.

        Purpose: Used for display and search indexing.
        """
        return self.name or ""

    @property
    def idx_public_repositories_count(self) -> int:
        """
        Returns the count of public repositories owned by the organization.

        Purpose: Used for indexing to provide insight into the organization's activity.
        """
        return self.public_repositories_count

    @property
    def idx_url(self) -> str:
        """
        Returns the URL of the organization.

        Purpose: Used to link to the organization's profile from search results.
        """
        return self.url
