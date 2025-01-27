"""OWASP app sponsor mixins."""

from apps.owasp.models.mixins.common import GenericEntityMixin

class SponsorIndexMixin(GenericEntityMixin):
    @property
    def idx_created_at(self):
        """Get created timestamp for index."""
        return self.nest_created_at

    @property
    def idx_updated_at(self):
        """Get updated timestamp for index."""
        return self.nest_updated_at

    @property
    def idx_name(self):
        """Get name for index."""
        return self.name

    @property
    def idx_sort_name(self):
        """Get sort name for index."""
        return self.sort_name

    @property
    def idx_description(self):
        """Get description for index."""
        return self.description

    @property
    def idx_url(self):
        """Get URL for index."""
        return self.url

    @property
    def idx_job_url(self):
        """Get job URL for index."""
        return self.job_url

    @property
    def idx_image(self):
        """Get image path for index."""
        return self.image

    @property
    def idx_member_type(self):
        """Get member type for index."""
        return self.member_type

    @property
    def idx_sponsor_type(self):
        """Get sponsor type for index."""
        return self.sponsor_type

    @property
    def idx_member_level(self):
        """Get member level for index."""
        return self.member_level

    @property
    def idx_sponsor_level(self):
        """Get sponsor level for index."""
        return self.sponsor_level

    @property
    def idx_is_member(self):
        """Get member status for index."""
        return self.is_member

    @property
    def idx_is_active_sponsor(self):
        """Get active sponsor status for index."""
        return self.is_active_sponsor