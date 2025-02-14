"""OWASP app committee mixins."""

#!/usr/bin/env python3
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
    def idx_top_contributors(self):
        """Return top contributors for indexing."""
        return super().get_top_contributors(repositories=[self.owasp_repository])

    @property
    def idx_updated_at(self):
        """Return updated at for indexing."""
        return self.updated_at.timestamp()
