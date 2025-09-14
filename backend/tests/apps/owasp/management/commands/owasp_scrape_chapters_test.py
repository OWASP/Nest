import os
from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_scrape_chapters import (
    Chapter,
    Command,
    normalize_url,
)


class TestOwaspScrapeChapters:
    @pytest.fixture
    def command(self):
        return Command()

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
    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.management.commands.owasp_scrape_chapters.get_github_client")
    def test_handle(self, mock_github, mock_bulk_save, command, mock_chapter, offset, chapters):
        mock_chapter.get_urls.return_value = [
            "https://example.com/repo1",
            "https://example.com/repo2",
            "https://invalid.com/repo3",
        ]
        mock_chapter.verify_url.side_effect = lambda url: None if "invalid" in url else url

        mock_chapter.get_related_url.side_effect = lambda url, **_: url

        mock_chapters_list = [mock_chapter] * chapters

        mock_active_chapters = mock.MagicMock()
        mock_active_chapters.__iter__.return_value = iter(mock_chapters_list)
        mock_active_chapters.count.return_value = len(mock_chapters_list)
        mock_active_chapters.__getitem__.side_effect = (
            lambda idx: mock_chapters_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_chapters_list[idx]
        )
        mock_active_chapters.order_by.return_value = mock_active_chapters

        mock_github_instance = mock.Mock()
        mock_github.return_value = mock_github_instance
        mock_github_instance.get_repo.return_value = mock.Mock()

        with (
            mock.patch.object(Chapter, "active_chapters", mock_active_chapters),
            mock.patch("builtins.print") as mock_print,
            mock.patch("time.sleep", return_value=None),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_chapters.normalize_url",
                side_effect=normalize_url,
            ),
        ):
            command.handle(offset=offset)

        mock_active_chapters.count.assert_called_once()

        assert mock_bulk_save.called

        assert mock_print.call_count == (chapters - offset)

        for call in mock_print.call_args_list:
            args, _ = call
            assert "https://owasp.org/www-chapter-test" in args[0]

        for chapter in mock_chapters_list:
            expected_invalid_urls = ["https://invalid.com/repo3"]
            expected_related_urls = ["https://example.com/repo1", "https://example.com/repo2"]
            assert chapter.invalid_urls == sorted(expected_invalid_urls)
            assert chapter.related_urls == sorted(expected_related_urls)
