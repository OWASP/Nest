"""OWASP app common mixins."""


class RepositoryBasedEntityModelMixin:
    """OWASP repository-based entity model mixin.

    Purpose:
        Provides common index-related fields for OWASP entities that are linked
        to repositories (projects, chapters, committees, etc.).
        Each property exposes standardized data for search indexing.
    """

    @property
    def is_indexable(self):
        """Return whether this entity should be indexed.

        Purpose:
            Determines if the entity is suitable for indexing.
            An entity is indexable only if it has one or more active repositories.
        """
        return self.has_active_repositories

    @property
    def idx_description(self):
        """Return description for indexing.

        Purpose:
            Provides a text description that helps search engines
            understand and match the entity's content.
        """
        return self.description

    @property
    def idx_leaders(self):
        """Return leaders for indexing.

        Purpose:
            Returns a list of leader names (excluding GitHub mentions),
            used for improving entity relevance in search.
        """
        return [leader for leader in self.leaders_raw if not leader.startswith("@")]

    @property
    def idx_name(self):
        """Return name for indexing.

        Purpose:
            Supplies the entity's official name for indexing and search.
        """
        return self.name

    @property
    def idx_summary(self):
        """Return summary for indexing.

        Purpose:
            Provides a shorter text summary for quick search matching.
        """
        return self.summary

    @property
    def idx_tags(self):
        """Return tags for indexing.

        Purpose:
            Returns a list of tag keywords to improve search filtering
            and topic classification.
        """
        return self.tags

    @property
    def idx_topics(self):
        """Return topics for indexing.

        Purpose:
            Supplies topic labels associated with the entity
            for classification and semantic search.
        """
        return self.topics

    @property
    def idx_url(self):
        """Return URL for indexing.

        Purpose:
            Provides the canonical OWASP page URL for the entity,
            used for linking from indexed results.
        """
        return self.owasp_url
