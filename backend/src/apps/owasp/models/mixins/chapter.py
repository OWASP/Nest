"""OWASP app chapter mixins."""

from __future__ import annotations

from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin


class ChapterIndexMixin(RepositoryBasedEntityModelMixin):
    """Chapter index mixin."""

    @property
    def is_indexable(self) -> bool:
        """Chapters to index."""
        return self.latitude is not None and self.longitude is not None

    @property
    def idx_country(self) -> str:
        """Return country for indexing."""
        return self.country

    @property
    def idx_created_at(self) -> str:
        """Return created at for indexing."""
        created_at = self.created_at
        if created_at is None and self.owasp_repository is not None:
            created_at = self.owasp_repository.created_at
        return created_at.isoformat() if created_at else ""

    @property
    def idx_geo_location(self) -> tuple[float, float]:
        """Return geographic location for indexing."""
        return self.latitude, self.longitude

    @property
    def idx_is_active(self) -> bool:
        """Return active status for indexing."""
        return self.is_active

    @property
    def idx_key(self) -> str:
        """Return key for indexing."""
        return self.key

    @property
    def idx_meetup_group(self) -> str:
        """Return meetup group for indexing."""
        return self.meetup_group

    @property
    def idx_postal_code(self) -> str:
        """Return postal code for indexing."""
        return self.postal_code

    @property
    def idx_region(self) -> str:
        """Return region for indexing."""
        return self.region

    @property
    def idx_related_urls(self) -> list:
        """Return related URLs for indexing."""
        return self.related_urls

    @property
    def idx_suggested_location(self) -> str:
        """Return suggested location for indexing."""
        return self.suggested_location if self.suggested_location != "None" else ""

    @property
    def idx_top_contributors(self) -> list:
        """Return top contributors for indexing."""
        return RepositoryContributor.get_top_contributors(chapter=self.key)

    @property
    def idx_updated_at(self) -> str:
        """Return updated at for indexing."""
        updated_at = self.updated_at
        if updated_at is None and self.owasp_repository is not None:
            updated_at = self.owasp_repository.updated_at
        return updated_at.isoformat() if updated_at else ""
