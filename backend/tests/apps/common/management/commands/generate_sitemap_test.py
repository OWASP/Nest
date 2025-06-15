"""Tests for the generate_sitemap Django management command."""

import io
import tempfile
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

import pytest
from django.core.management import call_command

from apps.common.management.commands.generate_sitemap import Command


class TestGenerateSitemapCommand:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.command = Command()
        self.output_dir = tempfile.TemporaryDirectory()
        yield
        self.output_dir.cleanup()

    @patch("apps.common.management.commands.generate_sitemap.Project")
    @patch("apps.common.management.commands.generate_sitemap.Command.save_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_sitemap_content")
    def test_generate_project_sitemap(self, mock_generate_content, mock_save, mock_project):
        mock_project.objects.all.return_value = [MagicMock(is_indexable=True, nest_key="foo")]
        mock_generate_content.return_value = "<xml>project</xml>"

        self.command.generate_project_sitemap(Path(self.output_dir.name))

        mock_save.assert_called_once()
        mock_generate_content.assert_called_once()

    @patch("apps.common.management.commands.generate_sitemap.Chapter")
    @patch("apps.common.management.commands.generate_sitemap.Command.save_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_sitemap_content")
    def test_generate_chapter_sitemap(self, mock_generate_content, mock_save, mock_chapter):
        mock_chapter.objects.filter.return_value = [MagicMock(is_indexable=True, nest_key="bar")]
        mock_generate_content.return_value = "<xml>chapter</xml>"

        self.command.generate_chapter_sitemap(Path(self.output_dir.name))

        mock_save.assert_called_once()
        mock_generate_content.assert_called_once()

    @patch("apps.common.management.commands.generate_sitemap.Committee")
    @patch("apps.common.management.commands.generate_sitemap.Command.save_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_sitemap_content")
    def test_generate_committee_sitemap(self, mock_generate_content, mock_save, mock_committee):
        mock_committee.objects.filter.return_value = [MagicMock(is_active=True, nest_key="baz")]
        mock_generate_content.return_value = "<xml>committee</xml>"

        self.command.generate_committee_sitemap(Path(self.output_dir.name))

        mock_save.assert_called_once()
        mock_generate_content.assert_called_once()

    @patch("apps.common.management.commands.generate_sitemap.User")
    @patch("apps.common.management.commands.generate_sitemap.Command.save_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_sitemap_content")
    def test_generate_user_sitemap(self, mock_generate_content, mock_save, mock_user):
        mock_user.objects.all.return_value = [MagicMock(is_indexable=True, login="user1")]
        mock_generate_content.return_value = "<xml>user</xml>"

        self.command.generate_user_sitemap(Path(self.output_dir.name))

        mock_save.assert_called_once()
        mock_generate_content.assert_called_once()

    def test_create_url_entry(self):
        url_data = {
            "loc": "https://example.com/foo",
            "lastmod": "2024-01-01",
            "changefreq": "weekly",
            "priority": "0.7",
        }
        entry = self.command.create_url_entry(url_data)

        assert "<loc>https://example.com/foo</loc>" in entry
        assert "<priority>0.7</priority>" in entry

    def test_create_sitemap_index_entry(self):
        sitemap_data = {"loc": "https://example.com/sitemap.xml", "lastmod": "2024-01-01"}
        entry = self.command.create_sitemap_index_entry(sitemap_data)

        assert "<loc>https://example.com/sitemap.xml</loc>" in entry

    def test_create_sitemap(self):
        urls = ["<url>foo</url>", "<url>bar</url>"]
        xml = self.command.create_sitemap(urls)

        assert "<urlset" in xml
        assert "foo" in xml
        assert "bar" in xml

    def test_create_sitemap_index(self):
        sitemaps = ["<sitemap>foo</sitemap>", "<sitemap>bar</sitemap>"]
        xml = self.command.create_sitemap_index(sitemaps)

        assert "<sitemapindex" in xml
        assert "foo" in xml
        assert "bar" in xml

    def test_save_sitemap(self):
        content = "<xml>test</xml>"
        path = Path(self.output_dir.name) / "test.xml"
        Command.save_sitemap(content, path)

        with Path.open(path, encoding="utf-8") as f:
            saved_content = f.read()

        assert saved_content == content

    @patch("apps.common.management.commands.generate_sitemap.Command.generate_chapter_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_committee_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_project_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_user_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.generate_index_sitemap")
    @patch("apps.common.management.commands.generate_sitemap.Command.save_sitemap")
    def test_handle_success(
        self, mock_save, mock_index, mock_user, mock_project, mock_committee, mock_chapter
    ):
        mock_index.return_value = "<xml>index</xml>"
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            call_command(
                "generate_sitemap",
                output_dir=self.output_dir.name,
            )
            output = fake_out.getvalue()

        assert "Successfully generated sitemaps" in output
        assert mock_save.called
        assert mock_index.called
        assert mock_user.called
        assert mock_project.called
        assert mock_committee.called
        assert mock_chapter.called

    def test_add_arguments(self):
        parser = MagicMock()
        self.command.add_arguments(parser)

        parser.add_argument.assert_called()

    def test_generate_sitemap_content_calls_create_url_entry_and_create_sitemap(self):
        self.command.create_url_entry = MagicMock(return_value="<url>mock</url>")
        self.command.create_sitemap = MagicMock(return_value="<xml>mock</xml>")
        routes = [
            {"path": "/foo", "changefreq": "daily", "priority": 1.0},
            {"path": "/bar", "changefreq": "weekly", "priority": 0.5},
        ]
        with patch("django.conf.settings.SITE_URL", "https://example.com"):
            result = self.command.generate_sitemap_content(routes)

        assert result == "<xml>mock</xml>"
        assert self.command.create_url_entry.call_count == 2

        self.command.create_url_entry.assert_any_call(
            {
                "loc": "https://example.com/foo",
                "lastmod": ANY,
                "changefreq": "daily",
                "priority": "1.0",
            }
        )
        self.command.create_sitemap.assert_called_once()

    def test_generate_index_sitemap_calls_create_sitemap_index_entry_and_create_sitemap_index(
        self,
    ):
        self.command.create_sitemap_index_entry = MagicMock(return_value="<sitemap>mock</sitemap>")
        self.command.create_sitemap_index = MagicMock(return_value="<xml>mockindex</xml>")
        files = ["sitemap-foo.xml", "sitemap-bar.xml"]
        with patch("django.conf.settings.SITE_URL", "https://example.com"):
            result = self.command.generate_index_sitemap(files)

        assert result == "<xml>mockindex</xml>"
        assert self.command.create_sitemap_index_entry.call_count == 2

        self.command.create_sitemap_index.assert_called_once()
