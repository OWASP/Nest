"""OWASP app committee mixins."""

from __future__ import annotations

from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin


class CommitteeIndexMixin(RepositoryBasedEntityModelMixin):
    """Committee index mixin."""

    @property
    def idx_created_at(self):
        """Return created at timestamp for indexing.

        Returns:
            float: The committee creation timestamp.

        """
        return self.created_at.timestamp()

    @property
    def idx_key(self):
        """Return key for indexing.

        Returns:
            str: The committee key without the 'www-committee-' prefix.

        """
        return self.key.replace("www-committee-", "")

    @property
    def idx_related_urls(self):
        """Return related URLs for indexing.

        Returns:
            list: A list of URLs related to the committee.

        """
        return self.related_urls

    @property
    def idx_top_contributors(self) -> list[str]:
        """Return top contributors for indexing.

        Returns:
            list[str]: A list of top contributor details for the committee.

        """
        return RepositoryContributor.get_top_contributors(committee=self.key)

    @property
    def idx_updated_at(self):
        """Return updated at timestamp for indexing.

        Returns:
            float: The committee's last update timestamp.

        """
        return self.updated_at.timestamp()
