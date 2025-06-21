"""GitHub organization mixins."""

from __future__ import annotations


class OrganizationIndexMixin:
    """Organization index mixin."""

    @property
    def is_indexable(self) -> bool:
        """Organizations to index."""
        return bool(self.is_owasp_related_organization and self.name and self.login)

    @property
    def idx_avatar_url(self) -> str:
        """Return avatar URL for indexing."""
        return self.avatar_url

    @property
    def idx_collaborators_count(self):
        """Return collaborators count for indexing.

        This calculates the total number of unique collaborators across all repositories
        owned by this organization.
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
        """Return created at for indexing."""
        return self.created_at.timestamp() if self.created_at else None

    @property
    def idx_description(self) -> str:
        """Return description for indexing."""
        return self.description or ""

    @property
    def idx_followers_count(self) -> int:
        """Return followers count for indexing."""
        return self.followers_count

    @property
    def idx_location(self) -> str:
        """Return location for indexing."""
        return self.location or ""

    @property
    def idx_login(self) -> str:
        """Return login for indexing."""
        return self.login

    @property
    def idx_name(self) -> str:
        """Return name for indexing."""
        return self.name or ""

    @property
    def idx_public_repositories_count(self) -> int:
        """Return public repositories count for indexing."""
        return self.public_repositories_count

    @property
    def idx_url(self) -> str:
        """Return URL for indexing."""
        return self.url
