"""OWASP app committee mixins."""

from __future__ import annotations

from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin


class CommitteeIndexMixin(RepositoryBasedEntityModelMixin):
    """Committee index mixin for OWASP projects."""

    @property
    def idx_created_at(self):
        """Return the creation timestamp of the committee.

        Purpose:
            Provides the created_at timestamp for indexing, allowing
            search engines or systems to sort/filter committees by creation date.
        """
        return self.created_at.timestamp()

    @property
    def idx_key(self):
        """Return the key of the committee.

        Purpose:
            Provides a unique identifier for indexing and search, removing
            the 'www-committee-' prefix for cleaner reference.
        """
        return self.key.replace("www-committee-", "")

    @property
    def idx_related_urls(self):
        """Return related URLs of the committee.

        Purpose:
            Supplies associated URLs for indexing to support
            navigation, references, or enrichment of search results.
        """
        return self.related_urls

    @property
    def idx_top_contributors(self) -> list[str]:
        """Return the top contributors for the committee.

        Purpose:
            Retrieves the list of top contributors for indexing, to highlight
            key contributors and support search relevance.
        """
        return RepositoryContributor.get_top_contributors(committee=self.key)

    @property
    def idx_updated_at(self):
        """Return the updated timestamp of the committee.

        Purpose:
            Provides the last updated timestamp for indexing, enabling
            search systems to rank or filter by recency of updates.
        """
        return self.updated_at.timestamp()
