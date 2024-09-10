"""OWASP app project mixins."""

from apps.common.utils import join_values


class ProjectIndexMixin:
    """Project index mixin."""

    @property
    def idx_companies(self):
        """Return companies for indexing."""
        return join_values(fields=(o.company for o in self.organizations.all()))

    @property
    def idx_created_at(self):
        """Return created at for indexing."""
        return self.created_at

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
        return self.languages

    @property
    def idx_leaders(self):
        """Return leaders for indexing."""
        return self.leaders_raw

    @property
    def idx_level(self):
        """Return level for indexing."""
        return float(self.level_raw) if self.level_raw else None

    @property
    def idx_organizations(self):
        """Return organizations for indexing."""
        return join_values(fields=(o.name for o in self.organizations.all()))

    @property
    def idx_name(self):
        """Return name for indexing."""
        return self.name

    @property
    def idx_stars_count(self):
        """Return stars count for indexing."""
        return self.stars_count

    @property
    def idx_tags(self):
        """Return tags for indexing."""
        return self.tags

    @property
    def idx_topics(self):
        """Return topics for indexing."""
        return self.topics

    @property
    def idx_type(self):
        """Return type for indexing."""
        return self.type

    @property
    def idx_updated_at(self):
        """Return updated at for indexing."""
        return self.updated_at

    @property
    def idx_url(self):
        """Return URL for indexing."""
        return self.owasp_url
