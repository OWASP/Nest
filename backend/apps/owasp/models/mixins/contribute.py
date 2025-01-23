"""OWASP app contribute mixins."""

from apps.owasp.models.mixins.common import GenericEntityMixin


class ContributeIndexMixin(GenericEntityMixin):
    """Contribute index mixin."""

    @property
    def idx_title(self):
        """Return the title for indexing."""
        return self.title

    @property
    def idx_project(self):
        """Return the project name for indexing."""
        return self.project.name if self.project else None

    @property
    def idx_project_url(self):
        """Return the project URL for indexing."""
        return self.project.url if self.project else None

    @property
    def idx_summary(self):
        """Return the summary for indexing."""
        return self.summary

    @property
    def idx_url(self):
        """Return the URL for indexing."""
        return self.url

    @property
    def idx_created_at(self):
        """Return created at for indexing."""
        return self.created_at.timestamp()

    @property
    def idx_key(self):
        """Return key for indexing."""
        return self.key.replace("www-contribute-", "")

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
