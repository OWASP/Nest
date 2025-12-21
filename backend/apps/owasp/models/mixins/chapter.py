"""OWASP app chapter mixins."""

from __future__ import annotations

from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin


class ChapterIndexMixin(RepositoryBasedEntityModelMixin):
    """Chapter index mixin."""

    @property
    def is_indexable(self) -> bool:
        """Determine if the chapter is indexable.

        Returns:
            bool: True if the chapter has valid geolocation, and the associated repository is not empty; False otherwise.
        """
        return (
            self.latitude is not None
            and self.longitude is not None
            and not self.owasp_repository.is_empty
        )

    @property
    def idx_country(self) -> str:
        """Return the country for indexing.

        Returns:
            str: The country associated with the chapter.
        """
        return self.country

    @property
    def idx_created_at(self) -> float:
        """Return the created at timestamp for indexing.

        Returns:
            float: The creation timestamp of the chapter or its repository.
        """
        return (self.created_at or self.owasp_repository.created_at).timestamp()

    @property
    def idx_geo_location(self) -> tuple[float, float]:
        """Return the geographic location for indexing.

        Returns:
            tuple[float, float]: A tuple of (latitude, longitude).
        """
        return self.latitude, self.longitude

    @property
    def idx_is_active(self) -> bool:
        """Return the active status for indexing.

        Returns:
            bool: True if the chapter is active, False otherwise.
        """
        return self.is_active

    @property
    def idx_key(self) -> str:
        """Return the key for indexing.

        Returns:
            str: The chapter key without the 'www-chapter-' prefix.
        """
        return self.key.replace("www-chapter-", "")

    @property
    def idx_meetup_group(self) -> str:
        """Return the meetup group for indexing.

        Returns:
            str: The name of the chapter's meetup group.
        """
        return self.meetup_group

    @property
    def idx_postal_code(self) -> str:
        """Return the postal code for indexing.

        Returns:
            str: The postal code of the chapter's location.
        """
        return self.postal_code

    @property
    def idx_region(self) -> str:
        """Return the region for indexing.

        Returns:
            str: The region associated with the chapter.
        """
        return self.region

    @property
    def idx_related_urls(self) -> list:
        """Return the related URLs for indexing.

        Returns:
            list: A list of URLs related to the chapter.
        """
        return self.related_urls

    @property
    def idx_suggested_location(self) -> str:
        """Return the suggested location for indexing.

        Returns:
            str: The suggested location string, or empty if 'None'.
        """
        return self.suggested_location if self.suggested_location != "None" else ""

    @property
    def idx_top_contributors(self) -> list:
        """Return the top contributors for indexing.

        Returns:
            list: A list of top contributors for the chapter.
        """
        return RepositoryContributor.get_top_contributors(chapter=self.key)

    @property
    def idx_updated_at(self) -> float:
        """Return the updated at timestamp for indexing.

        Returns:
            float: The last update timestamp of the chapter or its repository.
        """
        return (self.updated_at or self.owasp_repository.updated_at).timestamp()
