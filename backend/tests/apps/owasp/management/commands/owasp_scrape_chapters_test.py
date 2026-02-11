from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_scrape_chapters import (
    Chapter,
    Command,
    OwaspScraper,
    normalize_url,
)


class TestOwaspScrapeChapters:
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
    def mock_chapter(self):
        chapter = mock.Mock(spec=Chapter)
        chapter.owasp_url = "https://owasp.org/www-chapter-test"
        chapter.github_url = "https://github.com/owasp/test-chapter"
        chapter.get_related_url.side_effect = lambda url, **_: url
        chapter.invalid_urls = []
        chapter.related_urls = []
        return chapter

    @pytest.mark.parametrize(
        ("offset", "chapters"),
        [
            (0, 3),
            (2, 5),
            (0, 6),
            (1, 8),
        ],
    )
    @mock.patch.dict("os.environ", {"SCRAPER_API_KEY": "test-token"})
    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    def test_handle(self, mock_bulk_save, command, mock_chapter, offset, chapters):
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_chapter.get_urls.return_value = [
            "https://example.com/repo1",
            "https://example.com/repo2",
            "https://invalid.com/repo3",
        ]
        mock_scraper.verify_url.side_effect = lambda url: None if "invalid" in url else url
        mock_scraper.page_tree = True

        mock_chapter.get_related_url.side_effect = lambda url, **_: url

        mock_chapters_list = [mock_chapter] * chapters

        mock_active_chapters = mock.MagicMock()
        mock_active_chapters.__iter__.return_value = iter(mock_chapters_list)
        mock_active_chapters.count.return_value = len(mock_chapters_list)
        mock_active_chapters.__getitem__.side_effect = lambda idx: (
            mock_chapters_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_chapters_list[idx]
        )
        mock_active_chapters.order_by.return_value = mock_active_chapters

        with (
            mock.patch.object(Chapter, "active_chapters", mock_active_chapters),
            mock.patch("time.sleep", return_value=None),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_chapters.OwaspScraper",
                return_value=mock_scraper,
            ),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_chapters.normalize_url",
                side_effect=normalize_url,
            ),
        ):
            command.stdout = mock.MagicMock()
            command.handle(offset=offset)

        mock_active_chapters.count.assert_called_once()

        assert mock_bulk_save.called

        assert command.stdout.write.call_count == (chapters - offset)

        for call in command.stdout.write.call_args_list:
            args = call[0]
            assert "https://owasp.org/www-chapter-test" in args[0]

        for chapter in mock_chapters_list:
            expected_invalid_urls = ["https://invalid.com/repo3"]
            expected_related_urls = ["https://example.com/repo1", "https://example.com/repo2"]
            assert chapter.invalid_urls == sorted(expected_invalid_urls)
            assert chapter.related_urls == sorted(expected_related_urls)

    @mock.patch.dict("os.environ", {"SCRAPER_API_KEY": "test-token"})
    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    def test_handle_page_tree_none(self, mock_bulk_save, command, mock_chapter):
        """Test handle when scraper page_tree is None - chapter gets deactivated."""
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.page_tree = None

        mock_chapters_list = [mock_chapter]
        mock_active_chapters = mock.MagicMock()
        mock_active_chapters.__iter__.return_value = iter(mock_chapters_list)
        mock_active_chapters.count.return_value = 1
        mock_active_chapters.__getitem__.return_value = mock_chapters_list
        mock_active_chapters.order_by.return_value = mock_active_chapters

        with (
            mock.patch.object(Chapter, "active_chapters", mock_active_chapters),
            mock.patch("builtins.print"),
            mock.patch("time.sleep"),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_chapters.OwaspScraper",
                return_value=mock_scraper,
            ),
        ):
            command.handle(offset=0)

        mock_chapter.deactivate.assert_called_once()

    @mock.patch.dict("os.environ", {"SCRAPER_API_KEY": "test-token"})
    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    def test_handle_no_leaders_emails(self, mock_bulk_save, command, mock_chapter):
        """Test handle when chapter has no leaders emails."""
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.page_tree = True

        mock_chapter.get_leaders_emails.return_value = {}
        mock_chapter.get_urls.return_value = []

        mock_chapters_list = [mock_chapter]
        mock_active_chapters = mock.MagicMock()
        mock_active_chapters.__iter__.return_value = iter(mock_chapters_list)
        mock_active_chapters.count.return_value = 1
        mock_active_chapters.__getitem__.return_value = mock_chapters_list
        mock_active_chapters.order_by.return_value = mock_active_chapters

        with (
            mock.patch.object(Chapter, "active_chapters", mock_active_chapters),
            mock.patch("builtins.print"),
            mock.patch("time.sleep"),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_chapters.OwaspScraper",
                return_value=mock_scraper,
            ),
        ):
            command.handle(offset=0)

        mock_chapter.sync_leaders.assert_not_called()

    @mock.patch.dict("os.environ", {"SCRAPER_API_KEY": "test-token"})
    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    def test_handle_skipped_related_url(self, mock_bulk_save, command, mock_chapter):
        """Test handle when get_related_url returns None for verified URL."""
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.page_tree = True
        mock_scraper.verify_url.return_value = "https://example.com/verified"

        mock_chapter.get_leaders_emails.return_value = {}
        mock_chapter.get_urls.return_value = ["https://example.com/repo"]
        mock_chapter.get_related_url.side_effect = [
            "https://example.com/repo",
            None,
        ]

        mock_chapters_list = [mock_chapter]
        mock_active_chapters = mock.MagicMock()
        mock_active_chapters.__iter__.return_value = iter(mock_chapters_list)
        mock_active_chapters.count.return_value = 1
        mock_active_chapters.__getitem__.return_value = mock_chapters_list
        mock_active_chapters.order_by.return_value = mock_active_chapters

        with (
            mock.patch.object(Chapter, "active_chapters", mock_active_chapters),
            mock.patch("builtins.print"),
            mock.patch("time.sleep"),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_chapters.OwaspScraper",
                return_value=mock_scraper,
            ),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_chapters.normalize_url",
                side_effect=normalize_url,
            ),
        ):
            command.handle(offset=0)
