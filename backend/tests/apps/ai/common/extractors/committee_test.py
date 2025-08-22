"""Tests for committee content extractor."""

from unittest.mock import MagicMock

from apps.ai.common.extractors.committee import extract_committee_content


class TestCommitteeExtractor:
    """Test cases for committee content extraction."""

    def test_extract_committee_content_full_data(self):
        """Test extraction with complete committee data."""
        committee = MagicMock()
        committee.description = "Test committee description"
        committee.summary = "Test committee summary"
        committee.name = "Test Committee"
        committee.tags = ["governance", "policy"]
        committee.topics = ["Security Standards", "Best Practices"]
        committee.leaders_raw = ["Alice Johnson", "Bob Wilson"]
        committee.related_urls = ["https://committee.example.com"]
        committee.invalid_urls = []
        committee.is_active = True

        repo = MagicMock()
        repo.description = "Repository for committee resources"
        repo.topics = ["governance", "standards"]
        committee.owasp_repository = repo

        prose, metadata = extract_committee_content(committee)

        assert "Description: Test committee description" in prose
        assert "Summary: Test committee summary" in prose
        assert "Repository Description: Repository for committee resources" in prose

        assert "Committee Name: Test Committee" in metadata
        assert "Tags: governance, policy" in metadata
        assert "Topics: Security Standards, Best Practices" in metadata
        assert "Committee Leaders: Alice Johnson, Bob Wilson" in metadata
        assert "Related URLs: https://committee.example.com" in metadata
        assert "Active Committee: Yes" in metadata
        assert "Repository Topics: governance, standards" in metadata

    def test_extract_committee_content_minimal_data(self):
        """Test extraction with minimal committee data."""
        committee = MagicMock()
        committee.description = None
        committee.summary = None
        committee.name = "Minimal Committee"
        committee.tags = []
        committee.topics = []
        committee.leaders_raw = []
        committee.related_urls = []
        committee.invalid_urls = []
        committee.is_active = False
        committee.owasp_repository = None

        prose, metadata = extract_committee_content(committee)

        assert prose == ""
        assert "Committee Name: Minimal Committee" in metadata
        assert "Active Committee: No" in metadata

    def test_extract_committee_content_inactive_committee(self):
        """Test extraction with inactive committee."""
        committee = MagicMock()
        committee.description = "Inactive committee"
        committee.summary = None
        committee.name = "Inactive Committee"
        committee.tags = []
        committee.topics = []
        committee.leaders_raw = []
        committee.related_urls = []
        committee.invalid_urls = []
        committee.is_active = False
        committee.owasp_repository = None

        prose, metadata = extract_committee_content(committee)

        assert "Description: Inactive committee" in prose
        assert "Active Committee: No" in metadata

    def test_extract_committee_content_with_invalid_urls(self):
        """Test extraction with invalid URLs filtered out."""
        committee = MagicMock()
        committee.description = None
        committee.summary = None
        committee.name = "Test Committee"
        committee.tags = []
        committee.topics = []
        committee.leaders_raw = []
        committee.related_urls = ["https://valid.com", "https://invalid.com"]
        committee.invalid_urls = ["https://invalid.com"]
        committee.is_active = True
        committee.owasp_repository = None

        _, metadata = extract_committee_content(committee)

        assert "Related URLs: https://valid.com" in metadata
        assert "https://invalid.com" not in metadata

    def test_extract_committee_content_no_invalid_urls_attr(self):
        """Test extraction when invalid_urls attribute doesn't exist."""
        committee = MagicMock()
        committee.description = None
        committee.summary = None
        committee.name = "Test Committee"
        committee.tags = []
        committee.topics = []
        committee.leaders_raw = []
        committee.related_urls = ["https://valid.com"]
        committee.is_active = True
        committee.owasp_repository = None
        del committee.invalid_urls

        _, metadata = extract_committee_content(committee)

        assert "Related URLs: https://valid.com" in metadata

    def test_extract_committee_content_empty_strings(self):
        """Test extraction with empty string fields."""
        committee = MagicMock()
        committee.description = ""
        committee.summary = ""
        committee.name = ""
        committee.tags = []
        committee.topics = []
        committee.leaders_raw = []
        committee.related_urls = []
        committee.invalid_urls = []
        committee.is_active = True
        committee.owasp_repository = None

        prose, metadata = extract_committee_content(committee)

        assert prose == ""
        assert "Active Committee: Yes" in metadata
        assert "Committee Name:" not in metadata

    def test_extract_committee_content_repository_no_description(self):
        """Test extraction when repository has no description."""
        committee = MagicMock()
        committee.description = "Committee description"
        committee.summary = None
        committee.name = "Test Committee"
        committee.tags = []
        committee.topics = []
        committee.leaders_raw = []
        committee.related_urls = []
        committee.invalid_urls = []
        committee.is_active = True

        repo = MagicMock()
        repo.description = None
        repo.topics = ["topic1"]
        committee.owasp_repository = repo

        prose, metadata = extract_committee_content(committee)

        assert "Description: Committee description" in prose
        assert "Repository Description:" not in prose
        assert "Repository Topics: topic1" in metadata

    def test_extract_committee_content_repository_empty_topics(self):
        """Test extraction when repository has empty topics."""
        committee = MagicMock()
        committee.description = None
        committee.summary = None
        committee.name = "Test Committee"
        committee.tags = []
        committee.topics = []
        committee.leaders_raw = []
        committee.related_urls = []
        committee.invalid_urls = []
        committee.is_active = True

        repo = MagicMock()
        repo.description = "Repo description"
        repo.topics = []
        committee.owasp_repository = repo

        prose, metadata = extract_committee_content(committee)

        assert "Repository Description: Repo description" in prose
        assert "Repository Topics:" not in metadata

    def test_extract_committee_content_all_empty_after_filter(self):
        """Test extraction when all URLs are filtered out."""
        committee = MagicMock()
        committee.description = None
        committee.summary = None
        committee.name = "Test Committee"
        committee.tags = []
        committee.topics = []
        committee.leaders_raw = []
        committee.related_urls = ["https://invalid1.com", "https://invalid2.com"]
        committee.invalid_urls = ["https://invalid1.com", "https://invalid2.com"]
        committee.is_active = True
        committee.owasp_repository = None

        _, metadata = extract_committee_content(committee)

        assert "Related URLs:" not in metadata
