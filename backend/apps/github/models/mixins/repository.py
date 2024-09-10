"""GitHub repository mixins."""


class RepositoryIndexMixin:
    """Repository index mixin."""

    @property
    def idx_contributors_count(self):
        """Return contributors count for indexing."""
        return self.contributors_count

    @property
    def idx_description(self):
        """Return description for indexing."""
        return self.description

    @property
    def idx_forks_count(self):
        """Return forks count for indexing."""
        return self.forks_count

    @property
    def idx_languages(self):
        """Return languages for indexing."""
        return self.top_languages

    @property
    def idx_name(self):
        """Return name for indexing."""
        return self.name

    @property
    def idx_open_issues_count(self):
        """Return open issues count for indexing."""
        return self.open_issues_count

    @property
    def idx_pushed_at(self):
        """Return pushed at for indexing."""
        return self.pushed_at

    @property
    def idx_stars_count(self):
        """Return stars count for indexing."""
        return self.stars_count

    @property
    def idx_subscribers_count(self):
        """Return subscribers count for indexing."""
        return self.stars_count

    @property
    def idx_topics(self):
        """Return topics for indexing."""
        return self.topics
