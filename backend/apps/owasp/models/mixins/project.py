"""OWASP app project mixins."""

from django.db.models import Sum

from apps.common.utils import join_values
from apps.github.constants import OWASP_FOUNDATION_LOGIN
from apps.github.models.repository_contributor import (
    TOP_CONTRIBUTORS_LIMIT,
    RepositoryContributor,
)
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
    def idx_stars_count(self):
        """Return stars count for indexing."""
        return self.stars_count

    @property
    def idx_top_contributors(self):
        """Return top contributors for indexing."""
        return [
            {
                "avatar_url": tc["user__avatar_url"],
                "contributions_count": tc["total_contributions"],
                "login": tc["user__login"],
                "name": tc["user__name"],
            }
            for tc in RepositoryContributor.objects.filter(repository__in=self.repositories.all())
            .exclude(user__login__in=[OWASP_FOUNDATION_LOGIN])
            .values(
                "user__avatar_url",
                "user__login",
                "user__name",
            )
            .annotate(total_contributions=Sum("contributions_count"))
            .order_by("-total_contributions")[:TOP_CONTRIBUTORS_LIMIT]
        ]

    @property
    def idx_type(self):
        """Return type for indexing."""
        return self.type

    @property
    def idx_updated_at(self):
        """Return updated at for indexing."""
        return self.updated_at
