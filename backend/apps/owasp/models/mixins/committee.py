"""OWASP app committee mixins."""

from __future__ import annotations

from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin


class CommitteeIndexMixin(RepositoryBasedEntityModelMixin):
    """Committee index mixin."""

    @property
    def idx_created_at(self):
        """Return the created at timestamp for indexing.

        Returns:
            float: The creation timestamp of the committee.
        """
        return self.created_at.timestamp()

    @property
    def idx_key(self):
        """Return the key for indexing.

        Returns:
            str: The committee key without the 'www-committee-' prefix.
        """
        return self.key.replace("www-committee-", "")

    @property
    def idx_related_urls(self):
        """Return the related URLs for indexing.

        Returns:
            list: A list of URLs related to the committee.
        """
        return self.related_urls

    @property
    def idx_top_contributors(self) -> list[str]:
        """Return the top contributors for indexing.

        Returns:
            list[str]: A list of top contributors for the committee.
        """
        return RepositoryContributor.get_top_contributors(committee=self.key)

    @property
    def idx_updated_at(self):
        """Return the last update timestamp for indexing.

        Returns:
            float: The last update timestamp of the committee.
        """
        return self.updated_at.timestamp()
