"""GitHub organization mixins."""

from apps.common.utils import join_values


class OrganizationIndexMixin:
    """Organization index mixin."""

    @property
    def idx_name(self):
        """Return name for indexing."""
        return join_values((self.name, self.login))

    @property
    def idx_company(self):
        """Return company for indexing."""
        return join_values((self.company, self.location))
