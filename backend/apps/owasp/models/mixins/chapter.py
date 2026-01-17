"""OWASP app chapter mixins."""

from __future__ import annotations

from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.mixins.common import RepositoryBasedEntityModelMixin


class ChapterIndexMixin(RepositoryBasedEntityModelMixin):
    """Chapter index mixin."""

    @property
    def is_indexable(self) -> bool:
        """Determine if the chapter should be indexed.

        Returns:
            bool: True if the chapter meets indexing criteria, False otherwise.

        """
        return (
            self.latitude is not None
            and self.longitude is not None
            and not self.owasp_repository.is_empty
        )

    @property
    def idx_country(self) -> str:
        """Return country for indexing.

        Returns:
            str: The country where the chapter is located.

        """
        return self.country

    @property
    def idx_created_at(self) -> float:
        """Return created at timestamp for indexing.

        Returns:
            float: The chapter creation timestamp.

        """
        return (self.created_at or self.owasp_repository.created_at).timestamp()

    @property
    def idx_geo_location(self) -> tuple[float, float]:
        """Return geographic location for indexing.

        Returns:
            tuple[float, float]: The latitude and longitude of the chapter.

        """
        return self.latitude, self.longitude

    @property
    def idx_is_active(self) -> bool:
        """Return active status for indexing.

        Returns:
            bool: True if the chapter is active, False otherwise.

        """
        return self.is_active

    @property
    def idx_key(self) -> str:
        """Return key for indexing.

        Returns:
            str: The chapter key.

        """
        return self.key.replace("www-chapter-", "")

    @property
    def idx_meetup_group(self) -> str:
        """Return meetup group for indexing.

        Returns:
            str: The meetup group of the chapter.

        """
        return self.meetup_group

    @property
    def idx_postal_code(self) -> str:
        """Return postal code for indexing.

        Returns:
            str: The postal code of the chapter location.

        """
        return self.postal_code

    @property
    def idx_region(self) -> str:
        """Return region for indexing.

        Returns:
            str: The region where the chapter is located.

        """
        return self.region

    @property
    def idx_related_urls(self) -> list:
        """Return related URLs for indexing.

        Returns:
            list: A list of URLs related to the chapter.

        """
        return self.related_urls

    @property
    def idx_suggested_location(self) -> str:
        """Return suggested location for indexing.

        Returns:
            str: The suggested location for the chapter, or empty string.

        """
        return self.suggested_location if self.suggested_location != "None" else ""

    @property
    def idx_top_contributors(self) -> list:
        """Return top contributors for indexing.

        Returns:
            list: A list of top contributor details for the chapter.

        """
        return RepositoryContributor.get_top_contributors(chapter=self.key)

    @property
    def idx_updated_at(self) -> float:
        """Return updated at timestamp for indexing.

        Returns:
            float: The chapter's last update timestamp.

        """
        return (self.updated_at or self.owasp_repository.updated_at).timestamp()
