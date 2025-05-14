"""OWASP app committee mixins."""

from __future__ import annotations

from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin


class CommitteeIndexMixin(RepositoryBasedEntityModelMixin):
    """Committee index mixin."""

    @property
    def idx_created_at(self):
        """Return created at for indexing."""
        return self.created_at.timestamp()

    @property
    def idx_key(self):
        """Return key for indexing."""
        return self.key.replace("www-committee-", "")

    @property
    def idx_related_urls(self):
        """Return related URLs for indexing."""
        return self.related_urls

    @property
    def idx_top_contributors(self) -> list[str]:
        """Return top contributors for indexing."""
        return RepositoryContributor.get_top_contributors(committee=self.key)

    @property
    def idx_updated_at(self):
        """Return updated at for indexing."""
        return self.updated_at.timestamp()
