"""Tests for repository content extractor."""

import json
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from apps.ai.common.constants import DELIMITER
from apps.ai.common.extractors.repository import (
    extract_repository_content,
)


def create_mock_repository(**kwargs):
    """Create a properly configured mock repository."""
    repository = MagicMock()
    repository.name = kwargs.get("name")
    repository.key = kwargs.get("key")
    repository.description = kwargs.get("description")
    repository.homepage = kwargs.get("homepage")
    repository.license = kwargs.get("license")
    repository.topics = kwargs.get("topics", [])
    repository.is_archived = kwargs.get("is_archived", False)
    repository.is_empty = kwargs.get("is_empty", False)
    repository.is_owasp_repository = kwargs.get("is_owasp_repository", False)
    repository.is_owasp_site_repository = kwargs.get("is_owasp_site_repository", False)
    repository.is_funding_policy_compliant = kwargs.get("is_funding_policy_compliant", False)
    repository.has_funding_yml = kwargs.get("has_funding_yml", False)
    repository.funding_yml = kwargs.get("funding_yml", {})
    repository.pages_status = kwargs.get("pages_status")
    repository.has_downloads = kwargs.get("has_downloads", False)
    repository.has_issues = kwargs.get("has_issues", False)
    repository.has_pages = kwargs.get("has_pages", False)
    repository.has_projects = kwargs.get("has_projects", False)
    repository.has_wiki = kwargs.get("has_wiki", False)
    repository.commits_count = kwargs.get("commits_count")
    repository.contributors_count = kwargs.get("contributors_count")
    repository.forks_count = kwargs.get("forks_count")
    repository.open_issues_count = kwargs.get("open_issues_count")
    repository.stars_count = kwargs.get("stars_count")
    repository.subscribers_count = kwargs.get("subscribers_count")
    repository.watchers_count = kwargs.get("watchers_count")
    repository.created_at = kwargs.get("created_at")
    repository.updated_at = kwargs.get("updated_at")
    repository.pushed_at = kwargs.get("pushed_at")
    repository.track_issues = kwargs.get("track_issues", False)
    repository.default_branch = kwargs.get("default_branch")
    repository.organization = kwargs.get("organization")
    repository.owner = kwargs.get("owner")
    return repository


class TestRepositoryContentExtractor:
    """Test cases for repository content extraction."""

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_content_full_data(self, mock_get_content, mock_sleep):
        """Test extraction with complete repository data."""
        mock_get_content.return_value = "[]"

        organization = MagicMock()
        organization.login = "test-org"

        owner = MagicMock()
        owner.login = "test-user"

        repository = create_mock_repository(
            name="test-repo",
            key="test-repo-key",
            description="A test repository for testing purposes",
            homepage="https://test-repo.example.com",
            license="MIT",
            topics=["security", "testing", "python"],
            is_owasp_repository=True,
            is_owasp_site_repository=True,
            is_funding_policy_compliant=True,
            has_funding_yml=True,
            funding_yml={"github": "owasp"},
            pages_status="enabled",
            has_downloads=True,
            has_issues=True,
            has_pages=True,
            has_projects=True,
            has_wiki=True,
            commits_count=1500,
            contributors_count=25,
            forks_count=100,
            open_issues_count=15,
            stars_count=500,
            subscribers_count=50,
            watchers_count=75,
            created_at=datetime(2020, 1, 15, tzinfo=UTC),
            updated_at=datetime(2024, 6, 10, tzinfo=UTC),
            pushed_at=datetime(2024, 6, 9, tzinfo=UTC),
            track_issues=True,
            default_branch="main",
            organization=organization,
            owner=owner,
        )

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["name"] == "test-repo"
        assert data["key"] == "test-repo-key"
        assert data["description"] == "A test repository for testing purposes"
        assert data["homepage"] == "https://test-repo.example.com"
        assert data["license"] == "MIT"
        assert data["topics"] == ["security", "testing", "python"]
        assert data["status"]["owasp_repository"]
        assert data["status"]["owasp_site_repository"]
        assert data["funding"]["policy_compliant"]
        assert data["funding"]["has_funding_yml"]
        assert data["pages_status"] == "enabled"
        assert data["features"] == ["downloads", "issues", "pages", "projects", "wiki"]
        assert data["statistics"]["commits"] == 1500
        assert data["statistics"]["contributors"] == 25
        assert data["statistics"]["forks"] == 100
        assert data["statistics"]["open_issues"] == 15
        assert data["statistics"]["stars"] == 500
        assert data["statistics"]["subscribers"] == 50
        assert data["statistics"]["watchers"] == 75
        assert data["dates"]["created"] == "2020-01-15"
        assert data["dates"]["last_updated"] == "2024-06-10"
        assert data["dates"]["last_pushed"] == "2024-06-09"
        assert data["ownership"]["organization"] == "test-org"
        assert data["ownership"]["owner"] == "test-user"

        assert "Repository Name: test-repo" in metadata
        assert "Repository Key: test-repo-key" in metadata
        assert "Organization: test-org" in metadata
        assert "Owner: test-user" in metadata

    def test_extract_repository_content_minimal_data(self):
        """Test extraction with minimal repository data."""
        repository = create_mock_repository(name="minimal-repo", key="minimal-repo-key")

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["name"] == "minimal-repo"
        assert data["key"] == "minimal-repo-key"

        assert "Repository Name: minimal-repo" in metadata
        assert "Repository Key: minimal-repo-key" in metadata

    def test_extract_repository_content_archived_repository(self):
        """Test extraction with archived repository."""
        repository = create_mock_repository(
            name="archived-repo",
            key="archived-repo-key",
            description="This repository is archived",
            is_archived=True,
            is_owasp_repository=True,
        )

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["name"] == "archived-repo"
        assert data["key"] == "archived-repo-key"
        assert data["description"] == "This repository is archived"
        assert data["status"]["archived"]
        assert data["status"]["owasp_repository"]

        assert "Repository Name: archived-repo" in metadata
        assert "Repository Key: archived-repo-key" in metadata

    def test_extract_repository_content_empty_repository(self):
        """Test extraction with empty repository."""
        repository = create_mock_repository(
            name="empty-repo",
            key="empty-repo-key",
            description="This repository is empty",
            is_empty=True,
        )

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["name"] == "empty-repo"
        assert data["key"] == "empty-repo-key"
        assert data["description"] == "This repository is empty"
        assert data["status"]["empty"]

        assert "Repository Name: empty-repo" in metadata
        assert "Repository Key: empty-repo-key" in metadata

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_content_with_organization_only(self, mock_get_content, mock_sleep):
        """Test extraction when repository has organization but no owner."""
        mock_get_content.return_value = "[]"
        organization = MagicMock()
        organization.login = "test-org"

        repository = create_mock_repository(
            name="org-repo", key="org-repo-key", organization=organization
        )

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["name"] == "org-repo"
        assert data["key"] == "org-repo-key"
        assert data["ownership"]["organization"] == "test-org"
        assert "owner" not in data["ownership"]

        assert "Repository Name: org-repo" in metadata
        assert "Repository Key: org-repo-key" in metadata
        assert "Organization: test-org" in metadata

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_content_with_owner_only(self, mock_get_content, mock_sleep):
        """Test extraction when repository has owner but no organization."""
        mock_get_content.return_value = "[]"
        owner = MagicMock()
        owner.login = "test-user"

        repository = create_mock_repository(name="user-repo", key="user-repo-key", owner=owner)

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["name"] == "user-repo"
        assert data["key"] == "user-repo-key"
        assert data["ownership"]["owner"] == "test-user"
        assert "organization" not in data["ownership"]

        assert "Repository Name: user-repo" in metadata
        assert "Repository Key: user-repo-key" in metadata
        assert "Owner: test-user" in metadata

    def test_extract_repository_content_delimiter_usage(self):
        """Test that DELIMITER is used correctly between content parts."""
        repository = create_mock_repository(
            name="delimiter-test",
            key="delimiter-test-key",
            description="First description",
            homepage="https://example.com",
            license="MIT",
        )

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["name"] == "delimiter-test"
        assert data["key"] == "delimiter-test-key"
        assert data["description"] == "First description"
        assert data["homepage"] == "https://example.com"
        assert data["license"] == "MIT"

        expected_metadata = (
            f"Repository Name: delimiter-test{DELIMITER}Repository Key: delimiter-test-key"
        )
        assert metadata == expected_metadata


class TestRepositoryMarkdownContentExtractor:
    """Test cases for repository markdown content extraction."""

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_with_description(
        self, mock_get_content, mock_sleep
    ):
        """Test extraction with repository description."""
        organization = MagicMock()
        organization.login = "test-org"

        repository = create_mock_repository(
            name="test-repo",
            key="test-repo",
            description="Test repository with markdown content",
            default_branch="main",
            organization=organization,
        )

        mock_get_content.return_value = ""

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["description"] == "Test repository with markdown content"
        assert data["ownership"]["organization"] == "test-org"

        assert "Repository Name: test-repo" in metadata
        assert "Repository Key: test-repo" in metadata
        assert "Organization: test-org" in metadata

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_with_readme(self, mock_get_content, mock_sleep):
        """Test extraction with README.md file."""
        organization = MagicMock()
        organization.login = "test-org"

        repository = create_mock_repository(
            name="test-repo",
            key="test-repo",
            description="Test repository",
            default_branch="main",
            organization=organization,
        )

        mock_get_content.return_value = "# Test Repository\n\nThis is a test repository."

        json_content, _ = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["description"] == "Test repository"
        assert data["ownership"]["organization"] == "test-org"
        assert "markdown_content" in data
        assert "README.md" in data["markdown_content"]
        assert (
            data["markdown_content"]["README.md"]
            == "# Test Repository\n\nThis is a test repository."
        )

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_with_owner_fallback(
        self, mock_get_content, mock_sleep
    ):
        """Test extraction when organization is None, falls back to owner."""
        owner = MagicMock()
        owner.login = "test-user"

        repository = create_mock_repository(
            name="test-repo",
            key="test-repo",
            description="Test repository",
            default_branch="main",
            owner=owner,
        )

        mock_get_content.return_value = "# Test Repository\n\nThis is a test repository."

        json_content, _ = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["description"] == "Test repository"
        assert data["ownership"]["owner"] == "test-user"
        assert "markdown_content" in data
        assert "README.md" in data["markdown_content"]

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_with_default_branch_fallback(
        self, mock_get_content, mock_sleep
    ):
        """Test extraction when default_branch is None, falls back to 'main'."""
        organization = MagicMock()
        organization.login = "test-org"

        repository = create_mock_repository(
            name="test-repo",
            key="test-repo",
            description="Test repository",
            organization=organization,
        )

        mock_get_content.return_value = "# Test Repository\n\nThis is a test repository."

        json_content, _ = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["description"] == "Test repository"
        assert data["ownership"]["organization"] == "test-org"
        assert "markdown_content" in data
        assert "README.md" in data["markdown_content"]

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_multiple_files(
        self, mock_get_content, mock_sleep
    ):
        """Test extraction with multiple markdown files."""
        organization = MagicMock()
        organization.login = "test-org"

        repository = create_mock_repository(
            name="test-repo",
            key="test-repo",
            description="Test repository",
            default_branch="main",
            organization=organization,
        )

        def mock_content_side_effect(url):
            if "README.md" in url:
                return "# README Content"
            if "index.md" in url:
                return "# Index Content"
            if "info.md" in url:
                return "# Info Content"
            if "leaders.md" in url:
                return "# Leaders Content"
            return ""

        mock_get_content.side_effect = mock_content_side_effect

        json_content, _ = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["description"] == "Test repository"
        assert data["ownership"]["organization"] == "test-org"
        assert "markdown_content" in data
        assert "README.md" in data["markdown_content"]
        assert data["markdown_content"]["README.md"] == "# README Content"
        assert "index.md" in data["markdown_content"]
        assert data["markdown_content"]["index.md"] == "# Index Content"
        assert "info.md" in data["markdown_content"]
        assert data["markdown_content"]["info.md"] == "# Info Content"
        assert "leaders.md" in data["markdown_content"]
        assert data["markdown_content"]["leaders.md"] == "# Leaders Content"

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_file_fetch_exception(
        self, mock_get_content, mock_sleep
    ):
        """Test extraction when file fetching raises an exception."""
        organization = MagicMock()
        organization.login = "test-org"

        repository = create_mock_repository(
            name="test-repo",
            key="test-repo",
            description="Test repository",
            default_branch="main",
            organization=organization,
        )

        problematic_url = "https://raw.githubusercontent.com/test-org/test-repo/main/README.md"
        network_error_message = "Network error"

        def side_effect(url):
            if url == problematic_url:
                raise ValueError(network_error_message)
            return ""

        mock_get_content.side_effect = side_effect

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["description"] == "Test repository"
        assert data["ownership"]["organization"] == "test-org"
        assert "markdown_content" not in data

        assert "Repository Name: test-repo" in metadata
        assert "Repository Key: test-repo" in metadata
        assert "Organization: test-org" in metadata
        mock_get_content.assert_any_call(problematic_url)

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_empty_file_content(
        self, mock_get_content, mock_sleep
    ):
        """Test extraction when file content is empty or whitespace."""
        organization = MagicMock()
        organization.login = "test-org"

        repository = create_mock_repository(
            name="test-repo",
            key="test-repo",
            description="Test repository",
            default_branch="main",
            organization=organization,
        )

        mock_get_content.return_value = "   \n\n  "

        json_content, _ = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["description"] == "Test repository"
        assert data["ownership"]["organization"] == "test-org"
        assert "markdown_content" not in data

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_no_description(
        self, mock_get_content, mock_sleep
    ):
        """Test extraction when repository has no description."""
        organization = MagicMock()
        organization.login = "test-org"

        repository = create_mock_repository(
            name="test-repo",
            key="test-repo",
            description=None,
            default_branch="main",
            organization=organization,
        )

        mock_get_content.return_value = "# Test Repository\n\nThis is a test repository."

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["name"] == "test-repo"
        assert data["key"] == "test-repo"
        assert data["ownership"]["organization"] == "test-org"
        assert "markdown_content" in data
        assert "README.md" in data["markdown_content"]

        assert "Repository Name: test-repo" in metadata
        assert "Repository Key: test-repo" in metadata
        assert "Organization: test-org" in metadata

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_url_construction(
        self, mock_get_content, mock_sleep
    ):
        """Test that URLs are constructed correctly for file fetching."""
        organization = MagicMock()
        organization.login = "test-org"

        repository = create_mock_repository(
            name="test-repo",
            key="test-repo",
            description="Test repository",
            default_branch="develop",
            organization=organization,
        )

        mock_get_content.return_value = "# Test Content"

        extract_repository_content(repository)

        mock_get_content.assert_called()
        assert any(
            "https://raw.githubusercontent.com/test-org/test-repo/develop/" in str(call)
            for call in mock_get_content.call_args_list
        )

    def test_extract_repository_markdown_content_no_owner_or_org(self):
        """Test extraction when repository has neither organization nor owner."""
        repository = create_mock_repository(
            name="test-repo", key="test-repo", description="Test repository", default_branch="main"
        )

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["description"] == "Test repository"
        assert data["name"] == "test-repo"
        assert data["key"] == "test-repo"

        assert "Repository Name: test-repo" in metadata
        assert "Repository Key: test-repo" in metadata

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_no_key(self, mock_get_content, mock_sleep):
        """Test extraction when repository has no key."""
        mock_get_content.return_value = "[]"
        organization = MagicMock()
        organization.login = "test-org"

        repository = create_mock_repository(
            name="test-repo",
            key=None,
            description="Test repository",
            default_branch="main",
            organization=organization,
        )

        json_content, metadata = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["description"] == "Test repository"
        assert data["name"] == "test-repo"
        assert data["ownership"]["organization"] == "test-org"

        assert "Repository Name: test-repo" in metadata
        assert "Organization: test-org" in metadata

    @patch("time.sleep")
    @patch("apps.ai.common.extractors.repository.logger")
    @patch("apps.ai.common.extractors.repository.get_repository_file_content")
    def test_extract_repository_markdown_content_logs_debug_on_exception(
        self, mock_get_content, mock_logger, mock_sleep
    ):
        """Test that debug logging occurs when file fetching fails."""
        organization = MagicMock()
        organization.login = "test-org"

        repository = create_mock_repository(
            name="test-repo",
            key="test-repo",
            description="Test repository",
            default_branch="main",
            organization=organization,
        )

        error_trigger_url = "https://raw.githubusercontent.com/test-org/test-repo/main/README.md"
        error_message = "Test exception"

        def side_effect(url):
            if url == error_trigger_url:
                raise ValueError(error_message)
            return "[]"

        mock_get_content.side_effect = side_effect

        json_content, _ = extract_repository_content(repository)

        data = json.loads(json_content)
        assert data["description"] == "Test repository"
        assert data["ownership"]["organization"] == "test-org"

        mock_logger.debug.assert_called_once()
        debug_call_args = mock_logger.debug.call_args[0][0]
        assert "Failed to fetch markdown file" in debug_call_args
