import logging
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from apps.common.constants import NL
from apps.common.management.commands.generate_sitemap import Command

PROJECT_SITEMAP_URL_LIMIT = 10000
CHAPTER_SITEMAP_URL_LIMIT = 10000
USER_SITEMAP_URL_LIMIT = 10000
EXPECTED_URL_COUNT = 2
EXPECTED_ENTRY_COUNT = 2

sitemap_chapters_file = "sitemap-chapters.xml"
sitemap_committees_file = "sitemap-committees.xml"
sitemap_users_file = "sitemap-users.xml"
project_sitemap_content = "project sitemap content"
chapter_sitemap_content = "chapter sitemap content"
committee_sitemap_content = "committee sitemap content"
user_sitemap_content = "user sitemap content"
sitemap_content = "SITEMAP CONTENT"
index_content = "INDEX CONTENT"


@pytest.fixture()
def mock_file_open(monkeypatch):
    """Mock file open operations."""
    mock_file = MagicMock()
    mock_open = MagicMock(return_value=mock_file)
    monkeypatch.setattr("builtins.open", mock_open)
    return mock_open


@pytest.fixture()
def mock_models(monkeypatch):
    """Mock database models."""
    project1 = MagicMock(nest_key="project1", is_indexable=True)
    project2 = MagicMock(nest_key="project2", is_indexable=False)
    project3 = MagicMock(nest_key="project3", is_indexable=True)

    projects = MagicMock()
    projects.all.return_value = [project1, project2, project3]
    monkeypatch.setattr("apps.owasp.models.project.Project.objects", projects)

    chapter1 = MagicMock(nest_key="chapter1", is_indexable=True)
    chapter2 = MagicMock(nest_key="chapter2", is_indexable=False)
    chapter3 = MagicMock(nest_key="chapter3", is_indexable=True)

    chapters = MagicMock()
    chapters.filter.return_value = [chapter1, chapter2, chapter3]
    monkeypatch.setattr("apps.owasp.models.chapter.Chapter.objects", chapters)

    committee1 = MagicMock(nest_key="committee1")
    committee2 = MagicMock(nest_key="committee2")

    committees = MagicMock()
    committees.filter.return_value = [committee1, committee2]
    monkeypatch.setattr("apps.owasp.models.committee.Committee.objects", committees)

    user1 = MagicMock(login="user1", is_indexable=True)
    user2 = MagicMock(login="user2", is_indexable=False)
    user3 = MagicMock(login="user3", is_indexable=True)

    users = MagicMock()
    users.all.return_value = [user1, user2, user3]
    monkeypatch.setattr("apps.github.models.user.User.objects", users)

    return {
        "projects": [project1, project2, project3],
        "chapters": [chapter1, chapter2, chapter3],
        "committees": [committee1, committee2],
        "users": [user1, user2, user3],
    }


@pytest.fixture()
def temp_dir(tmp_path):
    """Create a temporary directory for test outputs."""
    return tmp_path


@override_settings(SITE_URL="https://example.com")
class TestSitemapCommand(SimpleTestCase):
    def test_add_arguments(self):
        """Test that arguments are added to the parser."""
        from apps.common.management.commands.generate_sitemap import Command

        parser = MagicMock()
        command = Command()
        command.add_arguments(parser)

        parser.add_argument.assert_called_once_with(
            "--output-dir",
            default=settings.STATIC_ROOT,
            help="Directory where sitemap files will be saved",
        )

    @pytest.fixture(autouse=True)
    def _inject_fixtures(self, caplog, request):
        """Make fixtures available to test methods."""
        self.temp_dir = request.getfixturevalue("temp_dir")
        self.mock_models = request.getfixturevalue("mock_models")
        self.mock_file_open = request.getfixturevalue("mock_file_open")

    @patch("apps.common.management.commands.generate_sitemap.Command.generate_chapter_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_committee_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_project_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_user_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_index_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.save_sitemap")
    def test_handle_main_flow(
        self,
        mock_save_sitemap,
        mock_index_sitemap,
        mock_user_sitemap,
        mock_project_sitemap,
        mock_committee_sitemap,
        mock_chapter_sitemap,
    ):
        """Test the main command handle flow."""
        from apps.common.management.commands.generate_sitemap import Command

        mock_index_sitemap.return_value = "index content"
        output_dir = self.temp_dir

        command = Command()
        command.stdout = MagicMock()
        command.style = MagicMock()
        command.style.SUCCESS.return_value = "Success message"

        command.handle(output_dir=str(output_dir))

        mock_chapter_sitemap.assert_called_once_with(output_dir)
        mock_committee_sitemap.assert_called_once_with(output_dir)
        mock_project_sitemap.assert_called_once_with(output_dir)
        mock_user_sitemap.assert_called_once_with(output_dir)

        expected_files = [
            sitemap_chapters_file,
            sitemap_committees_file,
            "sitemap-projects.xml",
            sitemap_users_file,
        ]
        mock_index_sitemap.assert_called_once_with(expected_files)

        mock_save_sitemap.assert_called_once_with("index content", output_dir / "sitemap.xml")

        command.stdout.write.assert_called_once_with("Success message")
        command.style.SUCCESS.assert_called_once_with(
            f"Successfully generated sitemaps in {output_dir}"
        )

    def test_generate_project_sitemap(self):
        """Test project sitemap generation."""
        from apps.common.management.commands.generate_sitemap import Command

        command = Command()

        with patch.object(
            command, "generate_sitemap_content"
        ) as mock_generate_content, patch.object(command, "save_sitemap") as mock_save:
            mock_generate_content.return_value = project_sitemap_content

            command.generate_project_sitemap(self.temp_dir)

            base_routes = command.static_routes["projects"]
            additional_routes = [
                {"path": "/projects/project1", "changefreq": "weekly", "priority": 0.7},
                {"path": "/projects/project3", "changefreq": "weekly", "priority": 0.7},
            ]

            mock_generate_content.assert_called_once()
            actual_routes = mock_generate_content.call_args[0][0]

            for route in base_routes:
                assert route in actual_routes, f"Base route {route} not found in actual routes"

            for route in additional_routes:
                assert (
                    route in actual_routes
                ), f"Additional route {route} not found in actual routes"

            mock_save.assert_called_once_with(
                project_sitemap_content, self.temp_dir / "sitemap-project.xml"
            )

    def test_generate_chapter_sitemap(self):
        """Test chapter sitemap generation."""
        from apps.common.management.commands.generate_sitemap import Command

        command = Command()

        with patch.object(
            command, "generate_sitemap_content"
        ) as mock_generate_content, patch.object(command, "save_sitemap") as mock_save:
            mock_generate_content.return_value = chapter_sitemap_content

            command.generate_chapter_sitemap(self.temp_dir)

            base_routes = command.static_routes["chapters"]
            additional_routes = [
                {"path": "/chapters/chapter1", "changefreq": "weekly", "priority": 0.7},
                {"path": "/chapters/chapter3", "changefreq": "weekly", "priority": 0.7},
            ]

            mock_generate_content.assert_called_once()
            actual_routes = mock_generate_content.call_args[0][0]

            for route in base_routes:
                assert route in actual_routes, f"Base route {route} not found in actual routes"

            for route in additional_routes:
                assert (
                    route in actual_routes
                ), f"Additional route {route} not found in actual routes"

            mock_save.assert_called_once_with(
                chapter_sitemap_content, self.temp_dir / sitemap_chapters_file
            )

    def test_generate_committee_sitemap(self):
        """Test committee sitemap generation."""
        from apps.common.management.commands.generate_sitemap import Command

        command = Command()

        with patch.object(
            command, "generate_sitemap_content"
        ) as mock_generate_content, patch.object(command, "save_sitemap") as mock_save:
            mock_generate_content.return_value = committee_sitemap_content

            command.generate_committee_sitemap(self.temp_dir)

            base_routes = command.static_routes["committees"]
            additional_routes = [
                {"path": "/committees/committee1", "changefreq": "weekly", "priority": 0.7},
                {"path": "/committees/committee2", "changefreq": "weekly", "priority": 0.7},
            ]

            mock_generate_content.assert_called_once()
            actual_routes = mock_generate_content.call_args[0][0]

            for route in base_routes:
                assert route in actual_routes, f"Base route {route} not found in actual routes"

            for route in additional_routes:
                assert (
                    route in actual_routes
                ), f"Additional route {route} not found in actual routes"

            mock_save.assert_called_once_with(
                committee_sitemap_content, self.temp_dir / sitemap_committees_file
            )

    def test_generate_user_sitemap(self):
        """Test user sitemap generation."""
        from apps.common.management.commands.generate_sitemap import Command

        command = Command()

        with patch.object(
            command, "generate_sitemap_content"
        ) as mock_generate_content, patch.object(command, "save_sitemap") as mock_save:
            mock_generate_content.return_value = user_sitemap_content

            command.generate_user_sitemap(self.temp_dir)

            base_routes = command.static_routes["users"]
            additional_routes = [
                {"path": "/community/users/user1", "changefreq": "weekly", "priority": 0.7},
                {"path": "/community/users/user3", "changefreq": "weekly", "priority": 0.7},
            ]

            mock_generate_content.assert_called_once()
            actual_routes = mock_generate_content.call_args[0][0]

            for route in base_routes:
                assert route in actual_routes, f"Base route {route} not found in actual routes"

            for route in additional_routes:
                assert (
                    route in actual_routes
                ), f"Additional route {route} not found in actual routes"

            mock_save.assert_called_once_with(
                user_sitemap_content, self.temp_dir / sitemap_users_file
            )

    @pytest.mark.freeze_time("2023-01-01")
    def test_generate_sitemap_content(self):
        """Test sitemap content generation."""
        from apps.common.management.commands.generate_sitemap import Command

        command = Command()

        with patch.object(command, "create_url_entry") as mock_create_url, patch.object(
            command, "create_sitemap"
        ) as mock_create_sitemap:
            mock_create_url.side_effect = lambda data: f"URL:{data['loc']}"
            mock_create_sitemap.return_value = sitemap_content

            routes = [
                {"path": "/test1", "changefreq": "daily", "priority": 0.9},
                {"path": "/test2", "changefreq": "weekly", "priority": 0.8},
            ]

            result = command.generate_sitemap_content(routes)

            assert mock_create_url.call_count == EXPECTED_URL_COUNT
            mock_create_url.assert_any_call(
                {
                    "loc": f"{settings.SITE_URL}/test1",
                    "lastmod": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "changefreq": "daily",
                    "priority": "0.9",
                }
            )
            mock_create_url.assert_any_call(
                {
                    "loc": f"{settings.SITE_URL}/test2",
                    "lastmod": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "changefreq": "weekly",
                    "priority": "0.8",
                }
            )

            mock_create_sitemap.assert_called_once_with(
                ["URL:https://example.com/test1", "URL:https://example.com/test2"]
            )

            assert result == sitemap_content

    @pytest.mark.freeze_time("2023-01-01")
    def test_generate_index_sitemap(self):
        """Test sitemap index generation."""
        from apps.common.management.commands.generate_sitemap import Command

        command = Command()

        with patch.object(
            command, "create_sitemap_index_entry"
        ) as mock_create_entry, patch.object(command, "create_sitemap_index") as mock_create_index:
            mock_create_entry.side_effect = lambda data: f"ENTRY:{data['loc']}"
            mock_create_index.return_value = index_content

            sitemap_files = ["file1.xml", "file2.xml"]

            result = command.generate_index_sitemap(sitemap_files)

            assert mock_create_entry.call_count == EXPECTED_ENTRY_COUNT
            mock_create_entry.assert_any_call(
                {
                    "loc": f"{settings.SITE_URL}/file1.xml",
                    "lastmod": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                }
            )
            mock_create_entry.assert_any_call(
                {
                    "loc": f"{settings.SITE_URL}/file2.xml",
                    "lastmod": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                }
            )

            mock_create_index.assert_called_once_with(
                ["ENTRY:https://example.com/file1.xml", "ENTRY:https://example.com/file2.xml"]
            )

            assert result == index_content

    def test_create_url_entry(self):
        """Test URL entry creation."""
        from apps.common.management.commands.generate_sitemap import Command

        command = Command()

        url_data = {
            "loc": "https://example.com/test",
            "lastmod": "2023-01-01",
            "changefreq": "daily",
            "priority": "0.8",
        }

        result = command.create_url_entry(url_data)

        expected = (
            "  <url>\n"
            "    <loc>https://example.com/test</loc>\n"
            "    <lastmod>2023-01-01</lastmod>\n"
            "    <changefreq>daily</changefreq>\n"
            "    <priority>0.8</priority>\n"
            "  </url>"
        )

        assert result == expected

    def test_create_sitemap_index_entry(self):
        """Test sitemap index entry creation."""
        from apps.common.management.commands.generate_sitemap import Command

        command = Command()

        sitemap_data = {"loc": "https://example.com/sitemap.xml", "lastmod": "2023-01-01"}

        result = command.create_sitemap_index_entry(sitemap_data)

        expected = (
            "  <sitemap>\n"
            "    <loc>https://example.com/sitemap.xml</loc>\n"
            "    <lastmod>2023-01-01</lastmod>\n"
            "  </sitemap>"
        )

        assert result == expected

    def test_create_sitemap(self):
        """Test sitemap creation."""
        from apps.common.management.commands.generate_sitemap import Command

        command = Command()

        urls = ["URL1", "URL2", "URL3"]

        result = command.create_sitemap(urls)

        expected = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{NL.join(urls)}\n"
            "</urlset>"
        )

        assert result == expected

    def test_create_sitemap_index(self):
        """Test sitemap index creation."""
        from apps.common.management.commands.generate_sitemap import Command

        command = Command()

        sitemaps = ["SITEMAP1", "SITEMAP2", "SITEMAP3"]

        result = command.create_sitemap_index(sitemaps)

        expected = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{NL.join(sitemaps)}\n"
            "</sitemapindex>"
        )

        assert result == expected

    def test_save_sitemap(self):
        """Test sitemap saving."""
        from apps.common.management.commands.generate_sitemap import Command

        content = "SITEMAP CONTENT"
        filepath = self.temp_dir / "test-sitemap.xml"

        with patch("pathlib.Path.open", return_value=MagicMock()) as mock_file_open:
            mock_file = mock_file_open.return_value.__enter__.return_value

            Command.save_sitemap(content, filepath)

            mock_file_open.assert_called_once_with("w", encoding="utf-8")

            mock_file.write.assert_called_once_with(content)

    def test_integration_with_call_command(self):
        """Test integration with Django's call_command."""
        with patch(
            "apps.common.management.commands.generate_sitemap.Command.handle"
        ) as mock_handle:
            mock_handle.return_value = None

            call_command("generate_sitemap", output_dir=str(self.temp_dir))

            mock_handle.assert_called_once()
            kwargs = mock_handle.call_args[1]
            assert kwargs["output_dir"] == str(self.temp_dir)


"""Tests for the generate_sitemap management command."""

EXPECTED_URL_COUNT = 2
EXPECTED_ENTRY_COUNT = 2


class TestGenerateSitemap:
    """Test suite for generate_sitemap command."""

    @pytest.fixture(autouse=True)
    def _inject_fixtures(self, caplog, request):
        """Make fixtures available to test methods."""
        self.temp_dir = request.getfixturevalue("temp_dir")
        self.caplog = caplog

        self.mock_models = request.getfixturevalue("mock_models")

        patcher1 = patch("apps.owasp.models.project.Project.objects")
        patcher2 = patch("apps.owasp.models.chapter.Chapter.objects")
        patcher3 = patch("apps.owasp.models.committee.Committee.objects")
        patcher4 = patch("apps.github.models.user.User.objects")

        self.mock_projects = patcher1.start()
        self.mock_chapters = patcher2.start()
        self.mock_committees = patcher3.start()
        self.mock_users = patcher4.start()

        self.mock_projects.all.return_value = self.mock_models["projects"]
        self.mock_chapters.filter.return_value = self.mock_models["chapters"]
        self.mock_committees.filter.return_value = self.mock_models["committees"]
        self.mock_users.all.return_value = self.mock_models["users"]

        yield
        patcher1.stop()
        patcher2.stop()
        patcher3.stop()
        patcher4.stop()

    def test_command_generate_project_sitemap(self):
        """Test generate_project_sitemap command."""
        command = Command()

        with (
            patch.object(command, "generate_sitemap_content") as mock_generate_content,
            patch.object(command, "save_sitemap") as mock_save,
        ):
            mock_generate_content.return_value = project_sitemap_content

            with self.caplog.at_level(logging.INFO):
                command.generate_project_sitemap(self.temp_dir)

            mock_generate_content.assert_called_once()
            mock_save.assert_called_once_with(
                project_sitemap_content, self.temp_dir / "sitemap-project.xml"
            )

    def test_command_generate_chapter_sitemap(self):
        """Test generate_chapter_sitemap command."""
        command = Command()

        with (
            patch.object(command, "generate_sitemap_content") as mock_generate_content,
            patch.object(command, "save_sitemap") as mock_save,
        ):
            mock_generate_content.return_value = chapter_sitemap_content

            with self.caplog.at_level(logging.INFO):
                command.generate_chapter_sitemap(self.temp_dir)

            mock_generate_content.assert_called_once()
            mock_save.assert_called_once_with(
                chapter_sitemap_content, self.temp_dir / sitemap_chapters_file
            )

    def test_command_generate_committee_sitemap(self):
        """Test generate_committee_sitemap command."""
        command = Command()

        with (
            patch.object(command, "generate_sitemap_content") as mock_generate_content,
            patch.object(command, "save_sitemap") as mock_save,
        ):
            mock_generate_content.return_value = committee_sitemap_content

            with self.caplog.at_level(logging.INFO):
                command.generate_committee_sitemap(self.temp_dir)

            mock_generate_content.assert_called_once()
            mock_save.assert_called_once_with(
                committee_sitemap_content, self.temp_dir / sitemap_committees_file
            )

    def test_command_generate_user_sitemap(self):
        """Test generate_user_sitemap command."""
        command = Command()

        with (
            patch.object(command, "generate_sitemap_content") as mock_generate_content,
            patch.object(command, "save_sitemap") as mock_save,
        ):
            mock_generate_content.return_value = user_sitemap_content

            with self.caplog.at_level(logging.INFO):
                command.generate_user_sitemap(self.temp_dir)

            mock_generate_content.assert_called_once()
            mock_save.assert_called_once_with(
                user_sitemap_content, self.temp_dir / sitemap_users_file
            )

    def test_generate_sitemap_content(self):
        """Test the generate_sitemap_content method."""
        command = Command()

        routes = [
            {"path": "/test1", "changefreq": "daily", "priority": 0.9},
            {"path": "/test2", "changefreq": "weekly", "priority": 0.8},
        ]

        with (
            patch.object(command, "create_url_entry") as mock_create_url,
            patch.object(command, "create_sitemap") as mock_create_sitemap,
        ):
            mock_create_url.side_effect = lambda data: f"URL:{data['loc']}"
            mock_create_sitemap.return_value = sitemap_content

            result = command.generate_sitemap_content(routes)

            assert mock_create_url.call_count == EXPECTED_URL_COUNT
            mock_create_url.assert_any_call(
                {
                    "loc": f"{settings.SITE_URL}/test1",
                    "lastmod": mock_create_url.call_args_list[0][0][0]["lastmod"],
                    "changefreq": "daily",
                    "priority": "0.9",
                }
            )
            mock_create_url.assert_any_call(
                {
                    "loc": f"{settings.SITE_URL}/test2",
                    "lastmod": mock_create_url.call_args_list[1][0][0]["lastmod"],
                    "changefreq": "weekly",
                    "priority": "0.8",
                }
            )

            mock_create_sitemap.assert_called_once()
            assert result == sitemap_content

    def test_generate_index_content(self):
        """Test generating the sitemap index content."""
        command = Command()
        sitemap_files = ["sitemap-chapters.xml", "sitemap-projects.xml"]

        with (
            patch.object(command, "create_sitemap_index_entry") as mock_create_entry,
            patch.object(command, "create_sitemap_index") as mock_create_index,
        ):
            mock_create_entry.side_effect = lambda data: f"ENTRY:{data['loc']}"
            mock_create_index.return_value = index_content

            result = command.generate_index_sitemap(sitemap_files)

            assert mock_create_entry.call_count == EXPECTED_ENTRY_COUNT

            mock_create_index.assert_called_once()
            assert result == index_content
