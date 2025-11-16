"""OWASP app chapter mixins."""

from __future__ import annotations

from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin


class ChapterIndexMixin(RepositoryBasedEntityModelMixin):
    """Chapter index mixin."""

    @property
    def is_indexable(self) -> bool:
        """Chapters to index."""
        return (
            self.latitude is not None
            and self.longitude is not None
            and not self.owasp_repository.is_empty
        )

    @property
    def idx_country(self) -> str:
        """Return country for indexing."""
        return self.country

    @property
    def idx_created_at(self) -> float:
        """Return created at for indexing."""
        return (self.created_at or self.owasp_repository.created_at).timestamp()
class ChapterIndexMixin(RepositoryBasedEntityModelMixin):
    """Chapter index mixin for OWASP projects."""

    @property
    def is_indexable(self) -> bool:
        """Determine if the chapter should be indexed.

        Purpose:
            Checks that the chapter has valid geographic coordinates and
            the associated repository is not empty, ensuring only relevant
            chapters are indexed.
        """
        return (
            self.latitude is not None
            and self.longitude is not None
            and not self.owasp_repository.is_empty
        )

    @property
    def idx_country(self) -> str:
        """Return the country of the chapter.

        Purpose:
            Provides country information for indexing and geolocation-based search.
        """
        return self.country

    @property
    def idx_created_at(self) -> float:
        """Return the creation timestamp for indexing.

        Purpose:
            Supplies the created_at timestamp (chapter or repository) to
            enable sorting or filtering by creation date in the index.
        """
        return (self.created_at or self.owasp_repository.created_at).timestamp()

    @property
    def idx_geo_location(self) -> tuple[float, float]:
        """Return geographic coordinates for indexing.

        Purpose:
            Provides latitude and longitude for geospatial indexing and
            location-based search queries.
        """
        return self.latitude, self.longitude

    @property
    def idx_is_active(self) -> bool:
        """Return the active status for indexing.

        Purpose:
            Indicates whether the chapter is active to filter only relevant entries.
        """
        return self.is_active

    @property
    def idx_key(self) -> str:
        """Return the chapter key for indexing.

        Purpose:
            Supplies a unique identifier for indexing, removing the
            'www-chapter-' prefix for cleaner reference.
        """
        return self.key.replace("www-chapter-", "")

    @property
    def idx_meetup_group(self) -> str:
        """Return the meetup group for indexing.

        Purpose:
            Provides meetup group information for enrichment and
            reference in the search index.
        """
        return self.meetup_group

    @property
    def idx_postal_code(self) -> str:
        """Return postal code for indexing.

        Purpose:
            Supplies postal code information for geolocation-based indexing.
        """
        return self.postal_code

    @property
    def idx_region(self) -> str:
        """Return region for indexing.

        Purpose:
            Provides region data for indexing to enhance filtering or search relevance.
        """
        return self.region

    @property
    def idx_related_urls(self) -> list:
        """Return related URLs for indexing.

        Purpose:
            Supplies related URLs to enrich search results and references.
        """
        return self.related_urls

    @property
    def idx_suggested_location(self) -> str:
        """Return suggested location for indexing.

        Purpose:
            Provides an alternative location for indexing if available,
            ensuring completeness of geolocation data.
        """
        return self.suggested_location if self.suggested_location != "None" else ""

    @property
    def idx_top_contributors(self) -> list:
        """Return top contributors for indexing.

        Purpose:
            Retrieves top contributors for the chapter to highlight
            key contributors and support search relevance.
        """
        return RepositoryContributor.get_top_contributors(chapter=self.key)

    @property
    def idx_updated_at(self) -> float:
        """Return updated timestamp for indexing.

        Purpose:
            Supplies the last updated timestamp (chapter or repository) to
            enable search systems to rank or filter by recency.
        """
        return (self.updated_at or self.owasp_repository.updated_at).timestamp()

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
        return self.key.replace("www-chapter-", "")

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
    def idx_updated_at(self) -> float:
        """Return updated at for indexing."""
        return (self.updated_at or self.owasp_repository.updated_at).timestamp()
