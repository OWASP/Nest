import os
from unittest import mock

import github
import pytest

from apps.owasp.management.commands.owasp_scrape_projects import (
    Command,
    OwaspScraper,
    Project,
    normalize_url,
)


class TestOwaspScrapeProjects:
    @pytest.fixture()
    def command(self):
        return Command()

    @pytest.fixture()
    def mock_project(self):
        project = mock.Mock(spec=Project)
        project.owasp_url = "https://owasp.org/www-project-test"
        project.github_url = "https://github.com/owasp/test-project"
        project.get_related_url.side_effect = lambda url, **_: url
        project.invalid_urls = []
        project.related_urls = []
        return project

    @pytest.mark.parametrize(
        ("offset", "projects"),
        [
            (0, 3),
            (2, 5),
            (0, 6),
            (1, 8),
        ],
    )
    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch.object(github, "Github", autospec=True)
    def test_handle(self, mock_github, mock_bulk_save, command, mock_project, offset, projects):
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.get_urls.return_value = [
            "https://github.com/org/repo1",
            "https://github.com/org/repo2",
            "https://invalid.com/repo3",
        ]
        mock_scraper.verify_url.side_effect = lambda url: (None if "invalid" in url else url)
        mock_scraper.get_leaders.return_value = "Leaders data"
        mock_scraper.page_tree = True

        mock_github_instance = mock.Mock()
        mock_github.return_value = mock_github_instance

        mock_gh_organization = mock.Mock()
        mock_gh_organization.get_repos.return_value = [
            mock.Mock(full_name="org/repo1"),
            mock.Mock(full_name="org/repo2"),
        ]
        mock_github_instance.get_organization.return_value = mock_gh_organization

        mock_project.get_related_url.side_effect = lambda url, **_: url

        mock_projects_list = [mock_project] * projects

        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.count.return_value = len(mock_projects_list)
        mock_active_projects.__getitem__.side_effect = lambda idx: (
            mock_projects_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_projects_list[idx]
        )
        mock_active_projects.order_by.return_value = mock_active_projects

        with (
            mock.patch.object(Project, "active_projects", mock_active_projects),
            mock.patch("builtins.print") as mock_print,
            mock.patch("time.sleep", return_value=None),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_projects.OwaspScraper",
                return_value=mock_scraper,
            ),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_projects.normalize_url",
                side_effect=normalize_url,
            ),
        ):
            command.handle(offset=offset)

        mock_active_projects.count.assert_called_once()

        assert mock_bulk_save.called

        assert mock_print.call_count == (projects - offset)

        for call in mock_print.call_args_list:
            args, _ = call
            assert "https://owasp.org/www-project-test" in args[0]

        for project in mock_projects_list:
            expected_invalid_urls = ["https://invalid.com/repo3"]
            expected_related_urls = [
                "https://github.com/org/repo1",
                "https://github.com/org/repo2",
            ]
            assert project.invalid_urls == sorted(expected_invalid_urls)
            assert project.related_urls == sorted(expected_related_urls)
            assert project.leaders_raw == "Leaders data"
