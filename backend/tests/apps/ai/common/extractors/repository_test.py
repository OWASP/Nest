"""Tests for repository content extractor."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from apps.ai.common.constants import DELIMITER
from apps.ai.common.extractors.repository import (
    extract_repository_content,
    extract_repository_markdown_content,
)


class TestRepositoryContentExtractor:
    """Test cases for repository content extraction."""

    def test_extract_repository_content_full_data(self):
        """Test extraction with complete repository data."""
        repository = MagicMock()
        repository.name = "test-repo"
        repository.key = "test-repo-key"
        repository.description = "A test repository for testing purposes"
        repository.homepage = "https://test-repo.example.com"
        repository.license = "MIT"
        repository.topics = ["security", "testing", "python"]
        repository.is_archived = False
        repository.is_empty = False
        repository.is_owasp_repository = True
        repository.is_owasp_site_repository = True
        repository.is_funding_policy_compliant = True
        repository.has_funding_yml = True
        repository.funding_yml = {"github": "owasp"}
        repository.pages_status = "enabled"
        repository.has_downloads = True
        repository.has_issues = True
        repository.has_pages = True
        repository.has_projects = True
        repository.has_wiki = True
        repository.commits_count = 1500
        repository.contributors_count = 25
        repository.forks_count = 100
        repository.open_issues_count = 15
        repository.stars_count = 500
        repository.subscribers_count = 50
        repository.watchers_count = 75
        repository.created_at = datetime(2020, 1, 15, tzinfo=UTC)
        repository.updated_at = datetime(2024, 6, 10, tzinfo=UTC)
        repository.pushed_at = datetime(2024, 6, 9, tzinfo=UTC)
        repository.track_issues = True

        organization = MagicMock()
        organization.login = "test-org"
        repository.organization = organization

        owner = MagicMock()
        owner.login = "test-user"
        repository.owner = owner

        prose, metadata = extract_repository_content(repository)

        assert "Description: A test repository for testing purposes" in prose

        assert "Repository Name: test-repo" in metadata
        assert "Repository Key: test-repo-key" in metadata
        assert "Homepage: https://test-repo.example.com" in metadata
        assert "License: MIT" in metadata
        assert "Topics: security, testing, python" in metadata
        assert "Repository Status: OWASP Repository, OWASP Site Repository" in metadata
        assert "Funding Policy Compliant" in metadata
        assert "Has FUNDING.yml" in metadata
        assert "Has FUNDING.yml Data" in metadata
        assert "Pages Status: enabled" in metadata
        assert "Repository Features: Downloads, Issues, Pages, Projects, Wiki" in metadata
        assert "Commits: 1500" in metadata
        assert "Contributors: 25" in metadata
        assert "Forks: 100" in metadata
        assert "Open Issues: 15" in metadata
        assert "Stars: 500" in metadata
        assert "Subscribers: 50" in metadata
        assert "Watchers: 75" in metadata
        assert "Created: 2020-01-15" in metadata
        assert "Last Updated: 2024-06-10" in metadata
        assert "Last Pushed: 2024-06-09" in metadata
        assert "Organization: test-org" in metadata
        assert "Owner: test-user" in metadata
        assert "Track Issues: True" in metadata

    def test_extract_repository_content_minimal_data(self):
        """Test extraction with minimal repository data."""
        repository = MagicMock()
        repository.name = "minimal-repo"
        repository.key = "minimal-repo-key"
        repository.description = None
        repository.homepage = None
        repository.license = None
        repository.topics = []
        repository.is_archived = False
        repository.is_empty = False
        repository.is_owasp_repository = False
        repository.is_owasp_site_repository = False
        repository.is_funding_policy_compliant = False
        repository.has_funding_yml = False
        repository.funding_yml = {}
        repository.pages_status = None
        repository.has_downloads = False
        repository.has_issues = False
        repository.has_pages = False
        repository.has_projects = False
        repository.has_wiki = False
        repository.commits_count = None
        repository.contributors_count = None
        repository.forks_count = None
        repository.open_issues_count = None
        repository.stars_count = None
        repository.subscribers_count = None
        repository.watchers_count = None
        repository.created_at = None
        repository.updated_at = None
        repository.pushed_at = None
        repository.organization = None
        repository.owner = None
        repository.track_issues = False

        prose, metadata = extract_repository_content(repository)

        assert prose == ""

        assert "Repository Name: minimal-repo" in metadata
        assert "Repository Key: minimal-repo-key" in metadata

    def test_extract_repository_content_archived_repository(self):
        """Test extraction with archived repository."""
        repository = MagicMock()
        repository.name = "archived-repo"
        repository.key = "archived-repo-key"
        repository.description = "This repository is archived"
        repository.is_archived = True
        repository.is_empty = False
        repository.is_owasp_repository = True
        repository.is_owasp_site_repository = False

        prose, metadata = extract_repository_content(repository)

        assert "Description: This repository is archived" in prose
        assert "Repository Status: Archived, OWASP Repository" in metadata

    def test_extract_repository_content_empty_repository(self):
        """Test extraction with empty repository."""
        repository = MagicMock()
        repository.name = "empty-repo"
        repository.key = "empty-repo-key"
        repository.description = "This repository is empty"
        repository.is_archived = False
        repository.is_empty = True
        repository.is_owasp_repository = False
        repository.is_owasp_site_repository = False

        prose, metadata = extract_repository_content(repository)

        assert "Description: This repository is empty" in prose
        assert "Repository Status: Empty" in metadata

    def test_extract_repository_content_with_organization_only(self):
        """Test extraction when repository has organization but no owner."""
        repository = MagicMock()
        repository.name = "org-repo"
        repository.key = "org-repo-key"
        repository.organization = MagicMock(login="test-org")
        repository.owner = None

        _, metadata = extract_repository_content(repository)

        assert "Organization: test-org" in metadata
        assert "Owner: " not in metadata

    def test_extract_repository_content_with_owner_only(self):
        """Test extraction when repository has owner but no organization."""
        repository = MagicMock()
        repository.name = "user-repo"
        repository.key = "user-repo-key"
        repository.organization = None
        repository.owner = MagicMock(login="test-user")

        _, metadata = extract_repository_content(repository)

        assert "Owner: test-user" in metadata
        assert "Organization: " not in metadata

    def test_extract_repository_content_delimiter_usage(self):
        """Test that DELIMITER is used correctly between content parts."""
        repository = MagicMock()
        repository.name = "delimiter-test"
        repository.key = "delimiter-test-key"
        repository.description = "First description"
        repository.homepage = "https://example.com"
        repository.license = "MIT"
        repository.topics = []
        repository.is_archived = False
        repository.is_empty = False
        repository.is_owasp_repository = False
        repository.is_owasp_site_repository = False
        repository.is_funding_policy_compliant = False
        repository.has_funding_yml = False
        repository.funding_yml = {}
        repository.pages_status = None
        repository.has_downloads = False
        repository.has_issues = False
        repository.has_pages = False
        repository.has_projects = False
        repository.has_wiki = False
        repository.commits_count = None
        repository.contributors_count = None
        repository.forks_count = None
        repository.open_issues_count = None
        repository.stars_count = None
        repository.subscribers_count = None
        repository.watchers_count = None
        repository.created_at = None
        repository.updated_at = None
        repository.pushed_at = None
        repository.organization = None
        repository.owner = None
        repository.track_issues = False

        prose, metadata = extract_repository_content(repository)

        expected_metadata = (
            f"Repository Name: delimiter-test{DELIMITER}"
            f"Repository Key: delimiter-test-key{DELIMITER}"
            f"Homepage: https://example.com{DELIMITER}"
            f"License: MIT"
        )
        assert metadata == expected_metadata

        expected_prose = "Description: First description"
        assert prose == expected_prose


class TestRepositoryMarkdownContentExtractor:
    """Test cases for repository markdown content extraction."""

    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_with_description(self, mock_get_content):
        """Test extraction with repository description."""
        repository = MagicMock()
        repository.description = "Test repository with markdown content"
        repository.organization = MagicMock(login="test-org")
        repository.key = "test-repo"
        repository.default_branch = "main"

        mock_get_content.return_value = ""

        prose, metadata = extract_repository_markdown_content(repository)

        assert "Repository Description: Test repository with markdown content" in prose
        assert metadata == ""

    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_with_readme(self, mock_get_content):
        """Test extraction with README.md file."""
        repository = MagicMock()
        repository.description = "Test repository"
        repository.organization = MagicMock(login="test-org")
        repository.key = "test-repo"
        repository.default_branch = "main"

        mock_get_content.return_value = "# Test Repository\n\nThis is a test repository."

        prose, _ = extract_repository_markdown_content(repository)

        assert "Repository Description: Test repository" in prose
        assert "## README.md" in prose
        assert "# Test Repository\n\nThis is a test repository." in prose

    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_with_owner_fallback(self, mock_get_content):
        """Test extraction when organization is None, falls back to owner."""
        repository = MagicMock()
        repository.description = "Test repository"
        repository.organization = None
        repository.owner = MagicMock(login="test-user")
        repository.key = "test-repo"
        repository.default_branch = "main"

        mock_get_content.return_value = "# Test Repository\n\nThis is a test repository."

        prose, _ = extract_repository_markdown_content(repository)

        assert "Repository Description: Test repository" in prose
        assert "## README.md" in prose

    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_with_default_branch_fallback(
        self, mock_get_content
    ):
        """Test extraction when default_branch is None, falls back to 'main'."""
        repository = MagicMock()
        repository.description = "Test repository"
        repository.organization = MagicMock(login="test-org")
        repository.key = "test-repo"
        repository.default_branch = None

        mock_get_content.return_value = "# Test Repository\n\nThis is a test repository."

        prose, _ = extract_repository_markdown_content(repository)

        assert "Repository Description: Test repository" in prose
        assert "## README.md" in prose

    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_multiple_files(self, mock_get_content):
        """Test extraction with multiple markdown files."""
        repository = MagicMock()
        repository.description = "Test repository"
        repository.organization = MagicMock(login="test-org")
        repository.key = "test-repo"
        repository.default_branch = "main"

        def mock_content_side_effect(url):
            if "README.md" in url:
                return "# README Content"
            if "CONTRIBUTING.md" in url:
                return "# Contributing Guidelines"
            if "CODE_OF_CONDUCT.md" in url:
                return "# Code of Conduct"
            return ""

        mock_get_content.side_effect = mock_content_side_effect

        prose, _ = extract_repository_markdown_content(repository)

        assert "Repository Description: Test repository" in prose
        assert "## README.md" in prose
        assert "# README Content" in prose
        assert "## CONTRIBUTING.md" in prose
        assert "# Contributing Guidelines" in prose
        assert "## CODE_OF_CONDUCT.md" in prose
        assert "# Code of Conduct" in prose

    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_file_fetch_exception(self, mock_get_content):
        """Test extraction when file fetching raises an exception."""
        repository = MagicMock()
        repository.description = "Test repository"
        repository.organization = MagicMock(login="test-org")
        repository.key = "test-repo"
        repository.default_branch = "main"

        mock_get_content.side_effect = ConnectionError("Network error")

        prose, metadata = extract_repository_markdown_content(repository)

        assert "Repository Description: Test repository" in prose
        assert metadata == ""

    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_empty_file_content(self, mock_get_content):
        """Test extraction when file content is empty or whitespace."""
        repository = MagicMock()
        repository.description = "Test repository"
        repository.organization = MagicMock(login="test-org")
        repository.key = "test-repo"
        repository.default_branch = "main"

        mock_get_content.return_value = "   \n\n  "

        prose, _ = extract_repository_markdown_content(repository)

        assert "Repository Description: Test repository" in prose
        assert "## README.md" not in prose

    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_no_description(self, mock_get_content):
        """Test extraction when repository has no description."""
        repository = MagicMock()
        repository.description = None
        repository.organization = MagicMock(login="test-org")
        repository.key = "test-repo"
        repository.default_branch = "main"

        mock_get_content.return_value = "# Test Repository\n\nThis is a test repository."

        prose, metadata = extract_repository_markdown_content(repository)

        assert "## README.md" in prose
        assert "# Test Repository\n\nThis is a test repository." in prose
        assert metadata == ""

    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_url_construction(self, mock_get_content):
        """Test that URLs are constructed correctly for file fetching."""
        repository = MagicMock()
        repository.description = "Test repository"
        repository.organization = MagicMock(login="test-org")
        repository.key = "test-repo"
        repository.default_branch = "develop"

        mock_get_content.return_value = "# Test Content"

        extract_repository_markdown_content(repository)

        mock_get_content.assert_called()
        assert any(
            "https://raw.githubusercontent.com/test-org/test-repo/develop/" in str(call)
            for call in mock_get_content.call_args_list
        )

    def test_extract_repository_markdown_content_no_owner_or_org(self):
        """Test extraction when repository has neither organization nor owner."""
        repository = MagicMock()
        repository.description = "Test repository"
        repository.organization = None
        repository.owner = None
        repository.key = "test-repo"
        repository.default_branch = "main"

        prose, metadata = extract_repository_markdown_content(repository)

        assert "Repository Description: Test repository" in prose
        assert metadata == ""

    def test_extract_repository_markdown_content_no_key(self):
        """Test extraction when repository has no key."""
        repository = MagicMock()
        repository.description = "Test repository"
        repository.organization = MagicMock(login="test-org")
        repository.key = None
        repository.default_branch = "main"

        prose, metadata = extract_repository_markdown_content(repository)

        assert "Repository Description: Test repository" in prose
        assert metadata == ""

    @patch("apps.ai.common.extractors.repository.logger")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_logs_debug_on_exception(
        self, mock_get_content, mock_logger
    ):
        """Test that debug logging occurs when file fetching fails."""
        repository = MagicMock()
        repository.description = "Test repository"
        repository.organization = MagicMock(login="test-org")
        repository.key = "test-repo"
        repository.default_branch = "main"

        mock_get_content.side_effect = ConnectionError("Test exception")

        prose, _ = extract_repository_markdown_content(repository)

        assert "Repository Description: Test repository" in prose
        mock_logger.debug.assert_called()
        debug_call_args = mock_logger.debug.call_args[0][0]
        assert "Failed to fetch" in debug_call_args
