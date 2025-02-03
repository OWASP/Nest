"""OWASP app common mixins."""


class RepositoryBasedEntityModelMixin:
    """OWASP repository based entity model mixin."""

    @property
    def is_indexable(self):
        """Entities to index."""
        return self.has_active_repositories

    @property
    def idx_description(self):
        """Return description for indexing."""
        return self.description

    @property
    def idx_leaders(self):
        """Return leaders for indexing."""
        return [leader for leader in self.leaders_raw if not leader.startswith("@")]

    @property
    def idx_name(self):
        """Return name for indexing."""
        return self.name

    @property
    def idx_summary(self):
        """Return summary for indexing."""
        return self.summary

    @property
    def idx_tags(self):
        """Return tags for indexing."""
        return self.tags

    @property
    def idx_topics(self):
        """Return topics for indexing."""
        return self.topics

    @property
    def idx_url(self):
        """Return URL for indexing."""
        return self.owasp_url
