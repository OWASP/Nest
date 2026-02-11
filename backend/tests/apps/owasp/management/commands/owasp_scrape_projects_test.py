import os
from unittest import mock

import pytest
from github.GithubException import UnknownObjectException

from apps.owasp.management.commands.owasp_scrape_projects import (
    Command,
    OwaspScraper,
    Project,
)


class TestOwaspScrapeProjects:
    @pytest.fixture
    def command(self):
        return Command()

    def test_add_arguments(self, command):
        """Test add_arguments adds expected arguments."""
        from argparse import ArgumentParser

        parser = ArgumentParser()
        command.add_arguments(parser)
        args = parser.parse_args([])
        assert args.offset == 0

    @pytest.fixture
    def mock_project(self):
        project = mock.Mock(spec=Project)
        project.owasp_url = "https://owasp.org/www-project-test"
        project.github_url = "https://github.com/owasp/test-project"
        project.get_related_url.side_effect = lambda url, **_: url
        project.audience = []
        project.invalid_urls = []
        project.related_urls = []
        return project

    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.management.commands.owasp_scrape_projects.get_github_client")
    def test_audience(self, mock_github, mock_bulk_save, command, mock_project):
        """Test audience validation logic."""
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.page_tree = True
        mock_project.get_urls.return_value = []
        mock_project.get_audience.return_value = ["builder", "breaker", "defender"]

        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter([mock_project])
        mock_active_projects.count.return_value = 1
        mock_active_projects.__getitem__.return_value = [mock_project]
        mock_active_projects.order_by.return_value = mock_active_projects

        with (
            mock.patch.object(Project, "active_projects", mock_active_projects),
            mock.patch("builtins.print"),
            mock.patch("time.sleep"),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_projects.OwaspScraper",
                return_value=mock_scraper,
            ),
        ):
            command.handle(offset=0)

        mock_bulk_save.assert_called_once()
        saved_project = mock_bulk_save.call_args[0][0][0]

        assert saved_project.audience == ["builder", "breaker", "defender"]

    @pytest.mark.parametrize(
        ("offset", "project_count"),
        [
            (0, 3),
            (2, 5),
        ],
    )
    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.management.commands.owasp_scrape_projects.get_github_client")
    def test_urls(self, mock_github, mock_bulk_save, command, mock_project, offset, project_count):
        """Tests the existing URL scraping logic, ensuring it still passes."""
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_project.get_urls.return_value = [
            "https://github.com/org/repo1",
            "https://github.com/org/repo2",
            "https://invalid.com/repo3",
        ]
        mock_project.get_audience.return_value = []
        mock_scraper.verify_url.side_effect = lambda url: None if "invalid" in url else url
        mock_scraper.page_tree = True

        mock_github_instance = mock.Mock()
        mock_github.return_value = mock_github_instance

        mock_gh_organization = mock.Mock()
        mock_gh_organization.get_repos.return_value = [
            mock.Mock(full_name="org/repo1"),
            mock.Mock(full_name="org/repo2"),
        ]
        mock_github_instance.get_organization.return_value = mock_gh_organization

        mock_projects_list = [mock_project] * project_count

        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.count.return_value = len(mock_projects_list)
        mock_active_projects.__getitem__.return_value = mock_projects_list[offset:]
        mock_active_projects.order_by.return_value = mock_active_projects

        with (
            mock.patch.object(Project, "active_projects", mock_active_projects),
            mock.patch("builtins.print") as mock_print,
            mock.patch("time.sleep", return_value=None),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_projects.OwaspScraper",
                return_value=mock_scraper,
            ),
        ):
            command.handle(offset=offset)

        assert mock_bulk_save.called
        assert mock_print.call_count == (project_count - offset)

        last_project = mock_bulk_save.call_args[0][0][-1]
        assert last_project.invalid_urls == ["https://invalid.com/repo3"]
        assert last_project.related_urls == [
            "https://github.com/org/repo1",
            "https://github.com/org/repo2",
        ]

    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.management.commands.owasp_scrape_projects.get_github_client")
    def test_handle_page_tree_none(self, mock_github, mock_bulk_save, command, mock_project):
        """Test handle when scraper page_tree is None - project gets deactivated."""
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.page_tree = None

        mock_projects_list = [mock_project]
        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.count.return_value = 1
        mock_active_projects.__getitem__.return_value = mock_projects_list
        mock_active_projects.order_by.return_value = mock_active_projects

        with (
            mock.patch.object(Project, "active_projects", mock_active_projects),
            mock.patch("builtins.print"),
            mock.patch("time.sleep"),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_projects.OwaspScraper",
                return_value=mock_scraper,
            ),
        ):
            command.handle(offset=0)

        mock_project.deactivate.assert_called_once()

    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.management.commands.owasp_scrape_projects.get_github_client")
    def test_handle_no_leaders_emails(self, mock_github, mock_bulk_save, command, mock_project):
        """Test handle when project has no leaders emails."""
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.page_tree = True

        mock_project.get_leaders_emails.return_value = {}
        mock_project.get_audience.return_value = []
        mock_project.get_urls.return_value = []

        mock_projects_list = [mock_project]
        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.count.return_value = 1
        mock_active_projects.__getitem__.return_value = mock_projects_list
        mock_active_projects.order_by.return_value = mock_active_projects

        with (
            mock.patch.object(Project, "active_projects", mock_active_projects),
            mock.patch("builtins.print"),
            mock.patch("time.sleep"),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_projects.OwaspScraper",
                return_value=mock_scraper,
            ),
        ):
            command.handle(offset=0)

        mock_project.sync_leaders.assert_not_called()

    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.management.commands.owasp_scrape_projects.get_github_client")
    def test_handle_github_user_unknown_object(self, mock_github, mock_bulk_save, command):
        """Test handle when GITHUB_USER_RE matches and get_organization raises."""
        mock_project = mock.Mock(spec=Project)
        mock_project.owasp_url = "https://owasp.org/www-project-test"
        mock_project.github_url = "https://github.com/owasp/test-project"
        mock_project.get_related_url.side_effect = lambda url, **_: url
        mock_project.get_audience.return_value = []
        mock_project.get_urls.return_value = ["https://github.com/some-org"]
        mock_project.get_leaders_emails.return_value = {}

        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.page_tree = True
        mock_scraper.verify_url.return_value = "https://github.com/some-org"

        mock_gh = mock.Mock()
        mock_gh.get_organization.side_effect = UnknownObjectException(
            status=404, data={"message": "Not Found"}
        )
        mock_github.return_value = mock_gh

        mock_projects_list = [mock_project]
        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.count.return_value = 1
        mock_active_projects.__getitem__.return_value = mock_projects_list
        mock_active_projects.order_by.return_value = mock_active_projects

        with (
            mock.patch.object(Project, "active_projects", mock_active_projects),
            mock.patch("builtins.print"),
            mock.patch("time.sleep"),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_projects.OwaspScraper",
                return_value=mock_scraper,
            ),
        ):
            command.handle(offset=0)

        mock_gh.get_organization.assert_called_once_with("some-org")

    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.management.commands.owasp_scrape_projects.get_github_client")
    def test_handle_skipped_related_url(self, mock_github, mock_bulk_save, command):
        """Test handle when get_related_url returns None for verified URL."""
        mock_project = mock.Mock(spec=Project)
        mock_project.owasp_url = "https://owasp.org/www-project-test"
        mock_project.github_url = "https://github.com/owasp/test-project"
        mock_project.get_audience.return_value = []
        mock_project.get_urls.return_value = ["https://example.com/repo"]
        mock_project.get_leaders_emails.return_value = {}
        mock_project.get_related_url.side_effect = [
            "https://example.com/repo",
            None,
        ]

        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.page_tree = True
        mock_scraper.verify_url.return_value = "https://example.com/repo"

        mock_github.return_value = mock.Mock()

        mock_projects_list = [mock_project]
        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.count.return_value = 1
        mock_active_projects.__getitem__.return_value = mock_projects_list
        mock_active_projects.order_by.return_value = mock_active_projects

        with (
            mock.patch.object(Project, "active_projects", mock_active_projects),
            mock.patch("builtins.print"),
            mock.patch("time.sleep"),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_projects.OwaspScraper",
                return_value=mock_scraper,
            ),
        ):
            command.handle(offset=0)
