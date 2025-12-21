"""OWASP app common mixins."""


class RepositoryBasedEntityModelMixin:
    """OWASP repository based entity model mixin."""

    @property
    def is_indexable(self):
        """Determine if the entity is indexable.

        Returns:
            bool: True if the entity has active repositories, False otherwise.
        """
        return self.has_active_repositories

    @property
    def idx_description(self):
        """Return the description for indexing.

        Returns:
            str: The description of the entity.
        """
        return self.description

    @property
    def idx_leaders(self):
        """Return the filtered leaders for indexing.

        Returns:
            list[str]: A list of leaders not starting with '@'.
        """
        return [leader for leader in self.leaders_raw if not leader.startswith("@")]

    @property
    def idx_name(self):
        """Return the name for indexing.

        Returns:
            str: The name of the entity.
        """
        return self.name

    @property
    def idx_summary(self):
        """Return the summary for indexing.

        Returns:
            str: The summary of the entity.
        """
        return self.summary

    @property
    def idx_tags(self):
        """Return the tags for indexing.

        Returns:
            list: A list of tags associated with the entity.
        """
        return self.tags

    @property
    def idx_topics(self):
        """Return the topics for indexing.

        Returns:
            list: A list of topics associated with the entity.
        """
        return self.topics

    @property
    def idx_url(self):
        """Return the OWASP URL for indexing.

        Returns:
            str: The OWASP URL of the entity.
        """
        return self.owasp_url
