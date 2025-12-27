"""OWASP app common mixins."""


class RepositoryBasedEntityModelMixin:
    """OWASP repository based entity model mixin."""

    @property
    def is_indexable(self):
        """Determine if the entity should be indexed.

        Returns:
            bool: True if the entity has active repositories, False otherwise.

        """
        return self.has_active_repositories

    @property
    def idx_description(self):
        """Return description for indexing.

        Returns:
            str: The entity description.

        """
        return self.description

    @property
    def idx_leaders(self):
        """Return leaders for indexing.

        Returns:
            list: A list of leader names, excluding those starting with '@'.

        """
        return [leader for leader in self.leaders_raw if not leader.startswith("@")]

    @property
    def idx_name(self):
        """Return name for indexing.

        Returns:
            str: The entity name.

        """
        return self.name

    @property
    def idx_summary(self):
        """Return summary for indexing.

        Returns:
            str: The entity summary.

        """
        return self.summary

    @property
    def idx_tags(self):
        """Return tags for indexing.

        Returns:
            list: A list of tags associated with the entity.

        """
        return self.tags

    @property
    def idx_topics(self):
        """Return topics for indexing.

        Returns:
            list: A list of topics associated with the entity.

        """
        return self.topics

    @property
    def idx_url(self):
        """Return URL for indexing.

        Returns:
            str: The OWASP URL for the entity.

        """
        return self.owasp_url
