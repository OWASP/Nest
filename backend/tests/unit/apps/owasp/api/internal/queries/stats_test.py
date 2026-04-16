"""Tests for StatsQuery."""

from unittest.mock import MagicMock, patch

from apps.owasp.api.internal.queries.stats import StatsQuery


class TestStatsQuery:
    """Test cases for StatsQuery."""

    def test_stats_overview_returns_node(self):
        """Test stats_overview returns StatsNode with calculated values."""
        mock_workspace = MagicMock()
        mock_workspace.total_members_count = 5500

        with (
            patch("apps.owasp.api.internal.queries.stats.Project") as mock_project,
            patch("apps.owasp.api.internal.queries.stats.Chapter") as mock_chapter,
            patch("apps.owasp.api.internal.queries.stats.User") as mock_user,
            patch("apps.owasp.api.internal.queries.stats.Workspace") as mock_workspace_cls,
        ):
            mock_project.active_projects_count.return_value = 275
            mock_chapter.active_chapters_count.return_value = 342
            mock_user.objects.count.return_value = 15234
            mock_filter = mock_chapter.objects.filter.return_value.exclude.return_value
            mock_filter.values.return_value.distinct.return_value.count.return_value = 98
            mock_workspace_cls.get_default_workspace.return_value = mock_workspace

            query = StatsQuery()
            result = query.stats_overview()

            assert result.active_projects_stats == 270
            assert result.active_chapters_stats == 340
            assert result.contributors_stats == 15000
            assert result.countries_stats == 90
            assert result.slack_workspace_stats == 5000

    def test_stats_overview_no_workspace(self):
        """Test stats_overview when no default workspace exists."""
        with (
            patch("apps.owasp.api.internal.queries.stats.Project") as mock_project,
            patch("apps.owasp.api.internal.queries.stats.Chapter") as mock_chapter,
            patch("apps.owasp.api.internal.queries.stats.User") as mock_user,
            patch("apps.owasp.api.internal.queries.stats.Workspace") as mock_workspace_cls,
        ):
            mock_project.active_projects_count.return_value = 10
            mock_chapter.active_chapters_count.return_value = 10
            mock_user.objects.count.return_value = 1000
            mock_filter = mock_chapter.objects.filter.return_value.exclude.return_value
            mock_filter.values.return_value.distinct.return_value.count.return_value = 10
            mock_workspace_cls.get_default_workspace.return_value = None

            query = StatsQuery()
            result = query.stats_overview()
            assert result.slack_workspace_stats == 0

    def test_stats_overview_has_strawberry_definition(self):
        """Check if StatsQuery has valid Strawberry definition."""
        assert hasattr(StatsQuery, "__strawberry_definition__")

        field_names = [field.name for field in StatsQuery.__strawberry_definition__.fields]
        assert "stats_overview" in field_names
