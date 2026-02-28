"""Tests for project content extractor."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

from apps.ai.common.extractors.project import extract_project_content


class TestProjectExtractor:
    """Test cases for project content extraction."""

    def test_extract_project_content_full_data(self):
        """Test extraction with complete project data."""
        project = MagicMock()
        project.description = "Test project description"
        project.summary = "Test project summary"
        project.name = "Test Project"
        project.level = "flagship"
        project.type = "tool"
        project.languages = ["Python", "JavaScript"]
        project.topics = ["security", "web-application-security"]
        project.licenses = ["MIT", "Apache-2.0"]
        project.tags = ["security", "testing"]
        project.custom_tags = ["owasp-top-10"]
        project.stars_count = 1500
        project.forks_count = 300
        project.contributors_count = 45
        project.releases_count = 12
        project.open_issues_count = 8
        project.leaders_raw = ["John Doe", "Jane Smith"]
        project.related_urls = ["https://project.example.com"]
        project.invalid_urls = []
        project.created_at = datetime(2020, 1, 15, tzinfo=UTC)
        project.updated_at = datetime(2024, 6, 10, tzinfo=UTC)
        project.released_at = datetime(2024, 5, 20, tzinfo=UTC)
        project.health_score = 85.75
        project.is_active = True

        repo = MagicMock()
        repo.description = "Repository for project resources"
        repo.topics = ["security", "python"]
        project.owasp_repository = repo

        prose, metadata = extract_project_content(project)

        assert "Description: Test project description" in prose
        assert "Summary: Test project summary" in prose
        assert "Repository Description: Repository for project resources" in prose

        assert "Project Name: Test Project" in metadata
        assert "Project Level: flagship" in metadata
        assert "Project Type: tool" in metadata
        assert "Programming Languages: Python, JavaScript" in metadata
        assert "Topics: security, web-application-security" in metadata
        assert "Licenses: MIT, Apache-2.0" in metadata
        assert "Tags: security, testing" in metadata
        assert "Custom Tags: owasp-top-10" in metadata
        assert (
            "Project Statistics: Stars: 1500, Forks: 300, Contributors: 45, "
            "Releases: 12, Open Issues: 8" in metadata
        )
        assert "Project Leaders: John Doe, Jane Smith" in metadata
        assert "Related URLs: https://project.example.com" in metadata
        assert "Created: 2020-01-15" in metadata
        assert "Last Updated: 2024-06-10" in metadata
        assert "Last Release: 2024-05-20" in metadata
        assert "Health Score: 85.75" in metadata
        assert "Active Project: Yes" in metadata
        assert "Repository Topics: security, python" in metadata

    def test_extract_project_content_minimal_data(self):
        """Test extraction with minimal project data."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "Minimal Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = []
        project.invalid_urls = []
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = False
        project.owasp_repository = None

        prose, metadata = extract_project_content(project)

        assert prose == ""
        assert "Project Name: Minimal Project" in metadata
        assert "Active Project: No" in metadata

    def test_extract_project_content_partial_statistics(self):
        """Test extraction with partial statistics."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "Partial Stats Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = 100
        project.forks_count = None
        project.contributors_count = 5
        project.releases_count = None
        project.open_issues_count = 3
        project.leaders_raw = []
        project.related_urls = []
        project.invalid_urls = []
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = True
        project.owasp_repository = None

        _, metadata = extract_project_content(project)

        assert "Project Statistics: Stars: 100, Contributors: 5, Open Issues: 3" in metadata

    def test_extract_project_content_zero_statistics(self):
        """Test extraction with zero values in statistics."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "Zero Stats Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = 0
        project.forks_count = 0
        project.contributors_count = 0
        project.releases_count = 0
        project.open_issues_count = 0
        project.leaders_raw = []
        project.related_urls = []
        project.invalid_urls = []
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = True
        project.owasp_repository = None

        _, metadata = extract_project_content(project)

        assert "Project Statistics:" not in metadata

    def test_extract_project_content_with_invalid_urls(self):
        """Test extraction with invalid URLs filtered out."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "URL Test Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = ["https://valid.com", "https://invalid.com"]
        project.invalid_urls = ["https://invalid.com"]
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = True
        project.owasp_repository = None

        _, metadata = extract_project_content(project)

        assert "Related URLs: https://valid.com" in metadata
        assert "https://invalid.com" not in metadata

    def test_extract_project_content_all_urls_invalid(self):
        """Test extraction when all related URLs are invalid."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "URL Test Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = ["https://invalid1.com", "https://invalid2.com"]
        project.invalid_urls = ["https://invalid1.com", "https://invalid2.com"]
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = True
        project.owasp_repository = None

        _, metadata = extract_project_content(project)
        assert "Related URLs:" not in metadata

    def test_extract_project_content_empty_urls_after_filter(self):
        """Test extraction when related_urls contains only empty strings or None."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "Empty URL Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = ["", None, ""]
        project.invalid_urls = []
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = True
        project.owasp_repository = None

        _, metadata = extract_project_content(project)

        assert "Related URLs:" not in metadata

    def test_extract_project_content_dates_only(self):
        """Test extraction with only date fields."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "Date Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = []
        project.invalid_urls = []
        project.created_at = datetime(2021, 3, 1, tzinfo=UTC)
        project.updated_at = None
        project.released_at = datetime(2023, 8, 15, tzinfo=UTC)
        project.health_score = None
        project.is_active = True
        project.owasp_repository = None

        _, metadata = extract_project_content(project)

        assert "Created: 2021-03-01" in metadata
        assert "Last Updated:" not in metadata
        assert "Last Release: 2023-08-15" in metadata

    def test_extract_project_content_health_score_zero(self):
        """Test extraction with zero health score."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "Zero Health Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = []
        project.invalid_urls = []
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = 0.0
        project.is_active = True
        project.owasp_repository = None

        _, metadata = extract_project_content(project)

        assert "Health Score: 0.00" in metadata

    def test_extract_project_content_repository_no_description(self):
        """Test extraction when repository has no description."""
        project = MagicMock()
        project.description = "Project description"
        project.summary = None
        project.name = "Test Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = []
        project.invalid_urls = []
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = True

        repo = MagicMock()
        repo.description = None
        repo.topics = ["security"]
        project.owasp_repository = repo

        prose, metadata = extract_project_content(project)

        assert "Description: Project description" in prose
        assert "Repository Description:" not in prose
        assert "Repository Topics: security" in metadata

    def test_extract_project_content_no_invalid_urls_attr(self):
        """Test extraction when invalid_urls attribute doesn't exist."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "Test Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = ["https://valid.com"]
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = True
        project.owasp_repository = None
        del project.invalid_urls

        _, metadata = extract_project_content(project)

        assert "Related URLs: https://valid.com" in metadata

    def test_extract_project_content_empty_strings(self):
        """Test extraction with empty string fields."""
        project = MagicMock()
        project.description = ""
        project.summary = ""
        project.name = ""
        project.level = ""
        project.type = ""
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = []
        project.invalid_urls = []
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = True
        project.owasp_repository = None

        prose, metadata = extract_project_content(project)

        assert prose == ""
        assert "Active Project: Yes" in metadata
        assert "Project Name:" not in metadata
        assert "Project Level:" not in metadata
        assert "Project Type:" not in metadata

    def test_extract_project_content_repository_with_topics_only(self):
        """Test extraction when repository has topics but no description."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "Test Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = []
        project.invalid_urls = []
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = True

        repo = MagicMock()
        repo.description = None
        repo.topics = ["security", "python"]
        project.owasp_repository = repo

        prose, metadata = extract_project_content(project)

        assert "Repository Description:" not in prose
        assert "Repository Topics: security, python" in metadata

    def test_extract_project_content_with_empty_related_urls(self):
        """Test extraction with related_urls containing empty strings."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "Test Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = ["https://valid.com", "", "https://another.com"]
        project.invalid_urls = []
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = True
        project.owasp_repository = None

        _, metadata = extract_project_content(project)

        assert "Related URLs: https://valid.com, https://another.com" in metadata

    def test_extract_project_content_repository_no_description_no_topics(self):
        """Test extraction when repository exists but has neither description nor topics."""
        project = MagicMock()
        project.description = "Project description"
        project.summary = None
        project.name = "Test Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = []
        project.invalid_urls = []
        project.created_at = None
        project.updated_at = None
        project.released_at = None
        project.health_score = None
        project.is_active = True

        repo = MagicMock()
        repo.description = None
        repo.topics = None
        project.owasp_repository = repo

        prose, metadata = extract_project_content(project)

        assert "Description: Project description" in prose
        assert "Repository Description:" not in prose
        assert "Repository Topics:" not in metadata

    def test_extract_project_content_created_and_released_only(self):
        """Test extraction with created_at and released_at but no updated_at."""
        project = MagicMock()
        project.description = None
        project.summary = None
        project.name = "Date Test Project"
        project.level = None
        project.type = None
        project.languages = []
        project.topics = []
        project.licenses = []
        project.tags = []
        project.custom_tags = []
        project.stars_count = None
        project.forks_count = None
        project.contributors_count = None
        project.releases_count = None
        project.open_issues_count = None
        project.leaders_raw = []
        project.related_urls = []
        project.invalid_urls = []
        project.created_at = datetime(2021, 3, 1, tzinfo=UTC)
        project.updated_at = None
        project.released_at = datetime(2023, 8, 15, tzinfo=UTC)
        project.health_score = None
        project.is_active = True
        project.owasp_repository = None

        _, metadata = extract_project_content(project)

        assert "Created: 2021-03-01" in metadata
        assert "Last Updated:" not in metadata
        assert "Last Release: 2023-08-15" in metadata
