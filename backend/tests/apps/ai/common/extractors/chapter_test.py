"""Tests for chapter content extractor."""

from unittest.mock import MagicMock

from apps.ai.common.extractors.chapter import extract_chapter_content


class TestChapterExtractor:
    """Test cases for chapter content extraction."""

    def test_extract_chapter_content_full_data(self):
        """Test extraction with complete chapter data."""
        chapter = MagicMock()
        chapter.description = "Test chapter description"
        chapter.summary = "Test chapter summary"
        chapter.name = "Test Chapter"
        chapter.country = "USA"
        chapter.region = "North America"
        chapter.postal_code = "12345"
        chapter.suggested_location = "New York, NY"
        chapter.currency = "USD"
        chapter.meetup_group = "owasp-nyc"
        chapter.tags = ["security", "web"]
        chapter.topics = ["OWASP Top 10", "Security Testing"]
        chapter.leaders_raw = ["John Doe", "Jane Smith"]
        chapter.related_urls = ["https://example.com", "https://github.com/test"]
        chapter.invalid_urls = []
        chapter.is_active = True

        repo = MagicMock()
        repo.description = "Repository for chapter resources"
        repo.topics = ["owasp", "security"]
        chapter.owasp_repository = repo

        prose, metadata = extract_chapter_content(chapter)

        assert "Description: Test chapter description" in prose
        assert "Summary: Test chapter summary" in prose
        assert "Repository Description: Repository for chapter resources" in prose

        assert "Chapter Name: Test Chapter" in metadata
        assert (
            "Location Information: Country: USA, Region: North America, "
            "Postal Code: 12345, Location: New York, NY" in metadata
        )
        assert "Currency: USD" in metadata
        assert "Meetup Group: owasp-nyc" in metadata
        assert "Tags: security, web" in metadata
        assert "Topics: OWASP Top 10, Security Testing" in metadata
        assert "Chapter Leaders: John Doe, Jane Smith" in metadata
        assert "Related URLs: https://example.com, https://github.com/test" in metadata
        assert "Active Chapter: Yes" in metadata
        assert "Repository Topics: owasp, security" in metadata

    def test_extract_chapter_content_minimal_data(self):
        """Test extraction with minimal chapter data."""
        chapter = MagicMock()
        chapter.description = None
        chapter.summary = None
        chapter.name = "Minimal Chapter"
        chapter.country = None
        chapter.region = None
        chapter.postal_code = None
        chapter.suggested_location = None
        chapter.currency = None
        chapter.meetup_group = None
        chapter.tags = []
        chapter.topics = []
        chapter.leaders_raw = []
        chapter.related_urls = []
        chapter.invalid_urls = []
        chapter.is_active = False
        chapter.owasp_repository = None

        prose, metadata = extract_chapter_content(chapter)

        assert prose == ""
        assert "Chapter Name: Minimal Chapter" in metadata
        assert "Description:" not in prose
        assert "Currency:" not in metadata
        assert "Active Chapter: Yes" not in metadata

    def test_extract_chapter_content_empty_fields(self):
        """Test extraction with empty string fields."""
        chapter = MagicMock()
        chapter.description = ""
        chapter.summary = ""
        chapter.name = ""
        chapter.country = ""
        chapter.region = ""
        chapter.postal_code = ""
        chapter.suggested_location = ""
        chapter.currency = ""
        chapter.meetup_group = ""
        chapter.tags = []
        chapter.topics = []
        chapter.leaders_raw = []
        chapter.related_urls = []
        chapter.invalid_urls = []
        chapter.is_active = False
        chapter.owasp_repository = None

        prose, metadata = extract_chapter_content(chapter)

        assert prose == ""
        assert metadata == ""

    def test_extract_chapter_content_partial_location(self):
        """Test extraction with partial location information."""
        chapter = MagicMock()
        chapter.description = None
        chapter.summary = None
        chapter.name = "Test Chapter"
        chapter.country = "Canada"
        chapter.region = None
        chapter.postal_code = "K1A 0A6"
        chapter.suggested_location = None
        chapter.currency = None
        chapter.meetup_group = None
        chapter.tags = []
        chapter.topics = []
        chapter.leaders_raw = []
        chapter.related_urls = []
        chapter.invalid_urls = []
        chapter.is_active = True
        chapter.owasp_repository = None

        prose, metadata = extract_chapter_content(chapter)

        assert prose == ""
        assert "Chapter Name: Test Chapter" in metadata
        assert "Location Information: Country: Canada, Postal Code: K1A 0A6" in metadata
        assert "Active Chapter: Yes" in metadata

    def test_extract_chapter_content_with_invalid_urls(self):
        """Test extraction with invalid URLs filtered out."""
        chapter = MagicMock()
        chapter.description = None
        chapter.summary = None
        chapter.name = "Test Chapter"
        chapter.country = None
        chapter.region = None
        chapter.postal_code = None
        chapter.suggested_location = None
        chapter.currency = None
        chapter.meetup_group = None
        chapter.tags = []
        chapter.topics = []
        chapter.leaders_raw = []
        chapter.related_urls = [
            "https://valid.com",
            "https://invalid.com",
            "https://another-valid.com",
        ]
        chapter.invalid_urls = ["https://invalid.com"]
        chapter.is_active = False
        chapter.owasp_repository = None

        _, metadata = extract_chapter_content(chapter)

        assert "Related URLs: https://valid.com, https://another-valid.com" in metadata
        assert "https://invalid.com" not in metadata

    def test_extract_chapter_content_repository_no_description(self):
        """Test extraction when repository has no description."""
        chapter = MagicMock()
        chapter.description = "Chapter description"
        chapter.summary = None
        chapter.name = "Test Chapter"
        chapter.country = None
        chapter.region = None
        chapter.postal_code = None
        chapter.suggested_location = None
        chapter.currency = None
        chapter.meetup_group = None
        chapter.tags = []
        chapter.topics = []
        chapter.leaders_raw = []
        chapter.related_urls = []
        chapter.invalid_urls = []
        chapter.is_active = False

        repo = MagicMock()
        repo.description = None
        repo.topics = ["security"]
        chapter.owasp_repository = repo

        prose, metadata = extract_chapter_content(chapter)

        assert "Description: Chapter description" in prose
        assert "Repository Description:" not in prose
        assert "Repository Topics: security" in metadata

    def test_extract_chapter_content_repository_empty_topics(self):
        """Test extraction when repository has empty topics."""
        chapter = MagicMock()
        chapter.description = "Chapter description"
        chapter.summary = None
        chapter.name = "Test Chapter"
        chapter.country = None
        chapter.region = None
        chapter.postal_code = None
        chapter.suggested_location = None
        chapter.currency = None
        chapter.meetup_group = None
        chapter.tags = []
        chapter.topics = []
        chapter.leaders_raw = []
        chapter.related_urls = []
        chapter.invalid_urls = []
        chapter.is_active = False

        repo = MagicMock()
        repo.description = "Repository description"
        repo.topics = []
        chapter.owasp_repository = repo

        prose, metadata = extract_chapter_content(chapter)

        assert "Description: Chapter description" in prose
        assert "Repository Description: Repository description" in prose
        assert "Repository Topics:" not in metadata

    def test_extract_chapter_content_none_invalid_urls(self):
        """Test extraction when invalid_urls is None."""
        chapter = MagicMock()
        chapter.description = None
        chapter.summary = None
        chapter.name = "Test Chapter"
        chapter.country = None
        chapter.region = None
        chapter.postal_code = None
        chapter.suggested_location = None
        chapter.currency = None
        chapter.meetup_group = None
        chapter.tags = []
        chapter.topics = []
        chapter.leaders_raw = []
        chapter.related_urls = ["https://valid.com"]
        chapter.invalid_urls = None
        chapter.is_active = False
        chapter.owasp_repository = None

        _, metadata = extract_chapter_content(chapter)

        assert "Related URLs: https://valid.com" in metadata

    def test_extract_chapter_content_empty_related_urls_after_filter(self):
        """Test extraction when all related URLs are invalid."""
        chapter = MagicMock()
        chapter.description = None
        chapter.summary = None
        chapter.name = "Test Chapter"
        chapter.country = None
        chapter.region = None
        chapter.postal_code = None
        chapter.suggested_location = None
        chapter.currency = None
        chapter.meetup_group = None
        chapter.tags = []
        chapter.topics = []
        chapter.leaders_raw = []
        chapter.related_urls = ["https://invalid1.com", "https://invalid2.com"]
        chapter.invalid_urls = ["https://invalid1.com", "https://invalid2.com"]
        chapter.is_active = False
        chapter.owasp_repository = None

        _, metadata = extract_chapter_content(chapter)

        assert "Related URLs:" not in metadata

    def test_extract_chapter_content_with_none_and_empty_urls(self):
        """Test extraction with mix of None and empty URLs."""
        chapter = MagicMock()
        chapter.description = None
        chapter.summary = None
        chapter.name = "Test Chapter"
        chapter.country = None
        chapter.region = None
        chapter.postal_code = None
        chapter.suggested_location = None
        chapter.currency = None
        chapter.meetup_group = None
        chapter.tags = []
        chapter.topics = []
        chapter.leaders_raw = []
        chapter.related_urls = [
            "https://valid.com",
            None,
            "",
            "https://another-valid.com",
        ]
        chapter.invalid_urls = []
        chapter.is_active = False
        chapter.owasp_repository = None

        _, metadata = extract_chapter_content(chapter)

        assert "Related URLs: https://valid.com, https://another-valid.com" in metadata
