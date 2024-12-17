"""OWASP app project mixins."""

from apps.common.utils import join_values
from apps.owasp.models.mixins.common import GenericEntityMixin


class ProjectIndexMixin(GenericEntityMixin):
    """Project index mixin."""

    @property
    def idx_companies(self):
        """Return companies for indexing."""
        return join_values(fields=(o.company for o in self.organizations.all()))

    @property
    def idx_contributors_count(self):
        """Return contributors count for indexing."""
        return self.contributors_count

    @property
    def idx_custom_tags(self):
        """Return custom tags for indexing."""
        return self.custom_tags

    @property
    def idx_forks_count(self):
        """Return forks count for indexing."""
        return self.forks_count

    @property
    def idx_languages(self):
        """Return languages for indexing."""
        return self.languages

    @property
    def idx_level(self):
        """Return level text value for indexing."""
        return self.level

    @property
    def idx_level_raw(self):
        """Return level for indexing."""
        return float(self.level_raw) if self.level_raw else None

    @property
    def idx_name(self):
        """Return name for indexing."""
        return self.name or " ".join(self.key.replace("www-project-", "").capitalize().split("-"))

    @property
    def idx_organizations(self):
        """Return organizations for indexing."""
        return join_values(fields=(o.name for o in self.organizations.all()))

    @property
    def idx_repository_descriptions(self):
        """Return repository descriptions for indexing.

        Description of the default OWASP project repository + 4 most recently updated repositories.
        """
        return [self.owasp_repository.description] + [
            repository.description
            for repository in self.repositories.exclude(id=self.owasp_repository.id)
            .exclude(description="")
            .order_by("-updated_at")[:4]
        ]

    @property
    def idx_repository_names(self):
        """Return repository names for indexing.

        Name of the default OWASP project repository + 4 most recently updated repositories.
        """
        return [self.owasp_repository.name] + [
            repository.name
            for repository in self.repositories.exclude(id=self.owasp_repository.id)
            .exclude(name="")
            .order_by("-updated_at")[:4]
        ]

    @property
    def idx_stars_count(self):
        """Return stars count for indexing."""
        return self.stars_count

    @property
    def idx_top_contributors(self):
        """Return top contributors for indexing."""
        return super().get_top_contributors(repositories=self.repositories.all())

    @property
    def idx_type(self):
        """Return type for indexing."""
        return self.type

    @property
    def idx_updated_at(self):
        """Return updated at for indexing."""
        return self.updated_at
