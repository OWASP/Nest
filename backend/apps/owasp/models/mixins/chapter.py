"""OWASP app project mixins."""


class ChapterIndexMixin:
    """Chapter index mixin."""

    @property
    def idx_country(self):
        """Return country for indexing."""
        return self.country

    @property
    def idx_geo_location(self):
        """Return geographic location for indexing."""
        return self.latitude, self.longitude

    @property
    def idx_meetup_group(self):
        """Return meetup group for indexing."""
        return self.meetup_group

    @property
    def idx_name(self):
        """Return name for indexing."""
        return self.name

    @property
    def idx_postal_code(self):
        """Return postal code for indexing."""
        return self.postal_code

    @property
    def idx_region(self):
        """Return region for indexing."""
        return self.region

    @property
    def idx_tags(self):
        """Return tags for indexing."""
        return self.tags

    @property
    def idx_url(self):
        """Return URL for indexing."""
        return self.owasp_url
