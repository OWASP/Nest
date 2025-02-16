"""OWASP app sponsor mixins."""

from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin


class SponsorIndexMixin(RepositoryBasedEntityModelMixin):
    """Sponsor index mixin."""

    @property
    def idx_created_at(self):
        """Get created timestamp for index."""
        return self.nest_created_at

    @property
    def idx_updated_at(self):
        """Get updated timestamp for index."""
        return self.nest_updated_at

    @property
    def idx_sort_name(self):
        """Get sort name for index."""
        return self.sort_name

    @property
    def idx_url(self):
        """Get URL for index."""
        return self.url

    @property
    def idx_job_url(self):
        """Get job URL for index."""
        return self.job_url

    @property
    def idx_image_path(self):
        """Get image path for index."""
        return self.image_path

    @property
    def idx_member_type(self):
        """Get member type for index."""
        return self.readable_member_type

    @property
    def idx_sponsor_type(self):
        """Get sponsor type for index."""
        return self.readable_sponsor_type

    @property
    def idx_is_member(self):
        """Get member status for index."""
        return self.is_member
