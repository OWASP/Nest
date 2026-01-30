"""Tests for ProjectIndexMixin."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from apps.owasp.models.mixins.project import (
    DEFAULT_HEALTH_SCORE,
    ProjectIndexMixin,
)


class TestProjectIndexMixin:
    """Test cases for ProjectIndexMixin."""

    def create_mock_project(self, **kwargs):
        """Create a mock project with ProjectIndexMixin methods."""
        mock_project = MagicMock(spec=ProjectIndexMixin)
        mock_project.key = kwargs.get("key", "www-project-test")
        mock_project.name = kwargs.get("name", "Test Project")
        mock_project.level = kwargs.get("level", "Lab")
        mock_project.level_raw = kwargs.get("level_raw", 2)
        mock_project.type = kwargs.get("type", "code")
        mock_project.custom_tags = kwargs.get("custom_tags", "security, testing")
        mock_project.languages = kwargs.get("languages", ["Python", "JavaScript"])
        mock_project.contributors_count = kwargs.get("contributors_count", 10)
        mock_project.forks_count = kwargs.get("forks_count", 5)
        mock_project.stars_count = kwargs.get("stars_count", 100)
        mock_project.is_active = kwargs.get("is_active", True)
        mock_project.health_score = kwargs.get("health_score", 85.5)
        mock_project.updated_at = kwargs.get(
            "updated_at", datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
        )

        # Mock related managers
        mock_project.organizations = MagicMock()
        mock_project.repositories = MagicMock()
        mock_project.open_issues = MagicMock()

        return mock_project

    def test_idx_companies(self):
        """Test idx_companies returns joined company names."""
        mock_org1 = MagicMock()
        mock_org1.company = "Company A"
        mock_org2 = MagicMock()
        mock_org2.company = "Company B"

        mock_project = self.create_mock_project()
        mock_project.organizations.all.return_value = [mock_org1, mock_org2]

        result = ProjectIndexMixin.idx_companies.fget(mock_project)

        assert "Company A" in result
        assert "Company B" in result

    def test_idx_contributors_count(self):
        """Test idx_contributors_count returns contributors count."""
        mock_project = self.create_mock_project(contributors_count=25)

        result = ProjectIndexMixin.idx_contributors_count.fget(mock_project)

        assert result == 25

    def test_idx_custom_tags(self):
        """Test idx_custom_tags returns custom tags."""
        mock_project = self.create_mock_project(custom_tags="api, web")

        result = ProjectIndexMixin.idx_custom_tags.fget(mock_project)

        assert result == "api, web"

    def test_idx_forks_count(self):
        """Test idx_forks_count returns forks count."""
        mock_project = self.create_mock_project(forks_count=42)

        result = ProjectIndexMixin.idx_forks_count.fget(mock_project)

        assert result == 42

    @patch("apps.owasp.models.mixins.project.settings")
    def test_idx_health_score_production(self, mock_settings):
        """Test idx_health_score returns default in production."""
        mock_settings.IS_PRODUCTION_ENVIRONMENT = True
        mock_project = self.create_mock_project(health_score=75.0)

        result = ProjectIndexMixin.idx_health_score.fget(mock_project)

        assert result == DEFAULT_HEALTH_SCORE

    @patch("apps.owasp.models.mixins.project.settings")
    def test_idx_health_score_non_production(self, mock_settings):
        """Test idx_health_score returns actual score in non-production."""
        mock_settings.IS_PRODUCTION_ENVIRONMENT = False
        mock_project = self.create_mock_project(health_score=75.0)

        result = ProjectIndexMixin.idx_health_score.fget(mock_project)

        assert result == pytest.approx(75.0)

    def test_idx_is_active(self):
        """Test idx_is_active returns active status."""
        mock_project = self.create_mock_project(is_active=True)

        result = ProjectIndexMixin.idx_is_active.fget(mock_project)

        assert result

    def test_idx_issues_count(self):
        """Test idx_issues_count returns open issues count."""
        mock_project = self.create_mock_project()
        mock_project.open_issues.count.return_value = 15

        result = ProjectIndexMixin.idx_issues_count.fget(mock_project)

        assert result == 15

    def test_idx_key(self):
        """Test idx_key strips www-project- prefix."""
        mock_project = self.create_mock_project(key="www-project-zap")

        result = ProjectIndexMixin.idx_key.fget(mock_project)

        assert result == "zap"

    def test_idx_languages(self):
        """Test idx_languages returns languages list."""
        mock_project = self.create_mock_project(languages=["Go", "Rust"])

        result = ProjectIndexMixin.idx_languages.fget(mock_project)

        assert result == ["Go", "Rust"]

    def test_idx_level(self):
        """Test idx_level returns level text."""
        mock_project = self.create_mock_project(level="Flagship")

        result = ProjectIndexMixin.idx_level.fget(mock_project)

        assert result == "Flagship"

    def test_idx_level_raw_with_value(self):
        """Test idx_level_raw returns float when level_raw exists."""
        mock_project = self.create_mock_project(level_raw=3)

        result = ProjectIndexMixin.idx_level_raw.fget(mock_project)

        assert result == pytest.approx(3.0)

    def test_idx_level_raw_none(self):
        """Test idx_level_raw returns None when level_raw is empty."""
        mock_project = self.create_mock_project(level_raw=None)

        result = ProjectIndexMixin.idx_level_raw.fget(mock_project)

        assert result is None

    def test_idx_name_with_name(self):
        """Test idx_name returns name when available."""
        mock_project = self.create_mock_project(name="OWASP ZAP")

        result = ProjectIndexMixin.idx_name.fget(mock_project)

        assert result == "OWASP ZAP"

    def test_idx_name_without_name(self):
        """Test idx_name generates name from key when name is empty."""
        mock_project = self.create_mock_project(name="", key="www-project-juice-shop")

        result = ProjectIndexMixin.idx_name.fget(mock_project)

        assert "juice" in result.lower()

    def test_idx_organizations(self):
        """Test idx_organizations returns joined organization names."""
        mock_org1 = MagicMock()
        mock_org1.name = "Org A"
        mock_org2 = MagicMock()
        mock_org2.name = "Org B"

        mock_project = self.create_mock_project()
        mock_project.organizations.all.return_value = [mock_org1, mock_org2]

        result = ProjectIndexMixin.idx_organizations.fget(mock_project)

        assert "Org A" in result
        assert "Org B" in result

    def test_idx_repositories(self):
        """Test idx_repositories returns repository dicts."""
        mock_release = MagicMock()
        mock_release.summary = "v1.0.0"

        mock_owner = MagicMock()
        mock_owner.login = "OWASP"

        mock_repo = MagicMock()
        mock_repo.contributors_count = 5
        mock_repo.description = "Test repo"
        mock_repo.forks_count = 2
        mock_repo.key = "TEST-REPO"
        mock_repo.latest_release = mock_release
        mock_repo.license = "MIT"
        mock_repo.name = "test-repo"
        mock_repo.owner = mock_owner
        mock_repo.stars_count = 50

        mock_project = self.create_mock_project()
        mock_project.repositories.order_by.return_value.__getitem__.return_value = [mock_repo]

        result = ProjectIndexMixin.idx_repositories.fget(mock_project)

        assert len(result) == 1
        assert result[0]["key"] == "test-repo"
        assert result[0]["owner_key"] == "owasp"

    def test_idx_repositories_no_release(self):
        """Test idx_repositories handles missing release."""
        mock_owner = MagicMock()
        mock_owner.login = "OWASP"

        mock_repo = MagicMock()
        mock_repo.contributors_count = 5
        mock_repo.description = "Test repo"
        mock_repo.forks_count = 2
        mock_repo.key = "TEST-REPO"
        mock_repo.latest_release = None
        mock_repo.license = "MIT"
        mock_repo.name = "test-repo"
        mock_repo.owner = mock_owner
        mock_repo.stars_count = 50

        mock_project = self.create_mock_project()
        mock_project.repositories.order_by.return_value.__getitem__.return_value = [mock_repo]

        result = ProjectIndexMixin.idx_repositories.fget(mock_project)

        assert result[0]["latest_release"] == ""

    def test_idx_repositories_count(self):
        """Test idx_repositories_count returns repository count."""
        mock_project = self.create_mock_project()
        mock_project.repositories.count.return_value = 3

        result = ProjectIndexMixin.idx_repositories_count.fget(mock_project)

        assert result == 3

    def test_idx_stars_count(self):
        """Test idx_stars_count returns stars count."""
        mock_project = self.create_mock_project(stars_count=500)

        result = ProjectIndexMixin.idx_stars_count.fget(mock_project)

        assert result == 500

    def test_idx_top_contributors(self):
        """Test idx_top_contributors calls RepositoryContributor."""
        mock_project = self.create_mock_project(key="www-project-test")

        with patch(
            "apps.owasp.models.mixins.project.RepositoryContributor.get_top_contributors"
        ) as mock_get:
            mock_get.return_value = [{"login": "user1"}, {"login": "user2"}]

            result = ProjectIndexMixin.idx_top_contributors.fget(mock_project)

            mock_get.assert_called_once_with(project="www-project-test")
            assert len(result) == 2

    def test_idx_type(self):
        """Test idx_type returns type."""
        mock_project = self.create_mock_project(type="documentation")

        result = ProjectIndexMixin.idx_type.fget(mock_project)

        assert result == "documentation"

    def test_idx_updated_at_with_datetime(self):
        """Test idx_updated_at returns timestamp when updated_at exists."""
        test_datetime = datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC)
        mock_project = self.create_mock_project(updated_at=test_datetime)

        result = ProjectIndexMixin.idx_updated_at.fget(mock_project)

        assert result == test_datetime.timestamp()

    def test_idx_updated_at_none(self):
        """Test idx_updated_at returns empty string when updated_at is None."""
        mock_project = self.create_mock_project(updated_at=None)

        result = ProjectIndexMixin.idx_updated_at.fget(mock_project)

        assert result == ""
