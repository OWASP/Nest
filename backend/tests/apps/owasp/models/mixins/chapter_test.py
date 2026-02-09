"""Tests for ChapterIndexMixin."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from apps.owasp.models.mixins.chapter import ChapterIndexMixin


class TestChapterIndexMixin:
    """Test cases for ChapterIndexMixin."""

    def create_mock_chapter(self, **kwargs):
        """Create a mock chapter with ChapterIndexMixin methods."""
        mock_chapter = MagicMock(spec=ChapterIndexMixin)
        mock_chapter.key = kwargs.get("key", "www-chapter-test")
        mock_chapter.name = kwargs.get("name", "Test Chapter")
        mock_chapter.country = kwargs.get("country", "United States")
        mock_chapter.region = kwargs.get("region", "California")
        mock_chapter.latitude = kwargs.get("latitude", 37.7749)
        mock_chapter.longitude = kwargs.get("longitude", -122.4194)
        mock_chapter.postal_code = kwargs.get("postal_code", "94102")
        mock_chapter.meetup_group = kwargs.get("meetup_group", "owasp-sf")
        mock_chapter.related_urls = kwargs.get("related_urls", ["https://example.com"])
        mock_chapter.suggested_location = kwargs.get("suggested_location", "San Francisco, CA")
        mock_chapter.is_active = kwargs.get("is_active", True)
        mock_chapter.created_at = kwargs.get(
            "created_at", datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
        )
        mock_chapter.updated_at = kwargs.get(
            "updated_at", datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
        )
        mock_repository = MagicMock()
        mock_repository.is_empty = kwargs.get("is_empty", False)
        mock_repository.created_at = datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC)
        mock_repository.updated_at = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
        mock_chapter.owasp_repository = mock_repository

        return mock_chapter

    def test_is_indexable_true(self):
        """Test is_indexable returns True when conditions are met."""
        mock_chapter = self.create_mock_chapter(
            latitude=37.7749, longitude=-122.4194, is_empty=False
        )

        result = ChapterIndexMixin.is_indexable.fget(mock_chapter)

        assert result

    def test_is_indexable_false_no_latitude(self):
        """Test is_indexable returns False when latitude is None."""
        mock_chapter = self.create_mock_chapter(latitude=None)

        result = ChapterIndexMixin.is_indexable.fget(mock_chapter)

        assert not result

    def test_is_indexable_false_no_longitude(self):
        """Test is_indexable returns False when longitude is None."""
        mock_chapter = self.create_mock_chapter(longitude=None)

        result = ChapterIndexMixin.is_indexable.fget(mock_chapter)

        assert not result

    def test_is_indexable_false_empty_repository(self):
        """Test is_indexable returns False when repository is empty."""
        mock_chapter = self.create_mock_chapter(is_empty=True)

        result = ChapterIndexMixin.is_indexable.fget(mock_chapter)

        assert not result

    def test_idx_country(self):
        """Test idx_country returns country."""
        mock_chapter = self.create_mock_chapter(country="Germany")

        result = ChapterIndexMixin.idx_country.fget(mock_chapter)

        assert result == "Germany"

    def test_idx_created_at_with_chapter_created_at(self):
        """Test idx_created_at returns chapter created_at timestamp."""
        test_datetime = datetime(2024, 3, 15, 10, 30, 0, tzinfo=UTC)
        mock_chapter = self.create_mock_chapter(created_at=test_datetime)

        result = ChapterIndexMixin.idx_created_at.fget(mock_chapter)

        assert result == test_datetime.timestamp()

    def test_idx_created_at_fallback_to_repository(self):
        """Test idx_created_at falls back to repository created_at."""
        mock_chapter = self.create_mock_chapter(created_at=None)

        result = ChapterIndexMixin.idx_created_at.fget(mock_chapter)

        assert result == mock_chapter.owasp_repository.created_at.timestamp()

    def test_idx_geo_location(self):
        """Test idx_geo_location returns latitude, longitude tuple."""
        mock_chapter = self.create_mock_chapter(latitude=51.5074, longitude=-0.1278)

        result = ChapterIndexMixin.idx_geo_location.fget(mock_chapter)

        assert result == (51.5074, -0.1278)

    def test_idx_is_active(self):
        """Test idx_is_active returns is_active status."""
        mock_chapter = self.create_mock_chapter(is_active=True)

        result = ChapterIndexMixin.idx_is_active.fget(mock_chapter)

        assert result

    def test_idx_key(self):
        """Test idx_key strips www-chapter- prefix."""
        mock_chapter = self.create_mock_chapter(key="www-chapter-london")

        result = ChapterIndexMixin.idx_key.fget(mock_chapter)

        assert result == "london"

    def test_idx_meetup_group(self):
        """Test idx_meetup_group returns meetup group."""
        mock_chapter = self.create_mock_chapter(meetup_group="owasp-london")

        result = ChapterIndexMixin.idx_meetup_group.fget(mock_chapter)

        assert result == "owasp-london"

    def test_idx_postal_code(self):
        """Test idx_postal_code returns postal code."""
        mock_chapter = self.create_mock_chapter(postal_code="SW1A 1AA")

        result = ChapterIndexMixin.idx_postal_code.fget(mock_chapter)

        assert result == "SW1A 1AA"

    def test_idx_region(self):
        """Test idx_region returns region."""
        mock_chapter = self.create_mock_chapter(region="Greater London")

        result = ChapterIndexMixin.idx_region.fget(mock_chapter)

        assert result == "Greater London"

    def test_idx_related_urls(self):
        """Test idx_related_urls returns related URLs list."""
        urls = ["https://owasp.org", "https://meetup.com"]
        mock_chapter = self.create_mock_chapter(related_urls=urls)

        result = ChapterIndexMixin.idx_related_urls.fget(mock_chapter)

        assert result == urls

    def test_idx_suggested_location(self):
        """Test idx_suggested_location returns suggested location."""
        mock_chapter = self.create_mock_chapter(suggested_location="London, UK")

        result = ChapterIndexMixin.idx_suggested_location.fget(mock_chapter)

        assert result == "London, UK"

    def test_idx_suggested_location_none_string(self):
        """Test idx_suggested_location returns empty string for 'None'."""
        mock_chapter = self.create_mock_chapter(suggested_location="None")

        result = ChapterIndexMixin.idx_suggested_location.fget(mock_chapter)

        assert result == ""

    def test_idx_top_contributors(self):
        """Test idx_top_contributors calls RepositoryContributor."""
        mock_chapter = self.create_mock_chapter(key="www-chapter-test")

        with patch(
            "apps.owasp.models.mixins.chapter.RepositoryContributor.get_top_contributors"
        ) as mock_get:
            mock_get.return_value = [{"login": "user1"}, {"login": "user2"}]

            result = ChapterIndexMixin.idx_top_contributors.fget(mock_chapter)

            mock_get.assert_called_once_with(chapter="www-chapter-test")
            assert len(result) == 2

    def test_idx_updated_at_with_chapter_updated_at(self):
        """Test idx_updated_at returns chapter updated_at timestamp."""
        test_datetime = datetime(2024, 8, 20, 14, 0, 0, tzinfo=UTC)
        mock_chapter = self.create_mock_chapter(updated_at=test_datetime)

        result = ChapterIndexMixin.idx_updated_at.fget(mock_chapter)

        assert result == test_datetime.timestamp()

    def test_idx_updated_at_fallback_to_repository(self):
        """Test idx_updated_at falls back to repository updated_at."""
        mock_chapter = self.create_mock_chapter(updated_at=None)

        result = ChapterIndexMixin.idx_updated_at.fget(mock_chapter)

        assert result == mock_chapter.owasp_repository.updated_at.timestamp()
