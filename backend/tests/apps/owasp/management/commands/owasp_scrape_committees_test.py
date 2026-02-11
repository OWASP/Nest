from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_scrape_committees import (
    Command,
    Committee,
    OwaspScraper,
    normalize_url,
)


class TestOwaspScrapeCommittees:
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
    def mock_committee(self):
        committee = mock.Mock(spec=Committee)
        committee.owasp_url = "https://owasp.org/www-committee-test"
        committee.github_url = "https://github.com/owasp/test-committee"
        committee.get_related_url.side_effect = lambda url, **_: url
        committee.invalid_urls = []
        committee.related_urls = []
        return committee

    @pytest.mark.parametrize(
        ("offset", "committees"),
        [
            (0, 3),
            (2, 5),
            (0, 6),
            (1, 8),
        ],
    )
    @mock.patch.dict("os.environ", {"SCRAPER_API_KEY": "test-token"})
    @mock.patch.object(Committee, "bulk_save", autospec=True)
    def test_handle(self, mock_bulk_save, command, mock_committee, offset, committees):
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_committee.get_urls.return_value = [
            "https://example.com/repo1",
            "https://example.com/repo2",
            "https://invalid.com/repo3",
        ]
        mock_scraper.verify_url.side_effect = lambda url: None if "invalid" in url else url
        mock_scraper.page_tree = True

        mock_committee.get_related_url.side_effect = lambda url, **_: url

        mock_committees_list = [mock_committee] * committees

        mock_active_committees = mock.MagicMock()
        mock_active_committees.__iter__.return_value = iter(mock_committees_list)
        mock_active_committees.count.return_value = len(mock_committees_list)
        mock_active_committees.__getitem__.side_effect = lambda idx: (
            mock_committees_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_committees_list[idx]
        )
        mock_active_committees.order_by.return_value = mock_active_committees

        with (
            mock.patch.object(Committee, "active_committees", mock_active_committees),
            mock.patch("time.sleep", return_value=None),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_committees.OwaspScraper",
                return_value=mock_scraper,
            ),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_committees.normalize_url",
                side_effect=normalize_url,
            ),
        ):
            command.stdout = mock.MagicMock()
            command.handle(offset=offset)

        mock_active_committees.count.assert_called_once()

        assert mock_bulk_save.called

        assert command.stdout.write.call_count == (committees - offset)

        for call in command.stdout.write.call_args_list:
            args = call[0]
            assert "https://owasp.org/www-committee-test" in args[0]

        for committee in mock_committees_list:
            expected_invalid_urls = ["https://invalid.com/repo3"]
            expected_related_urls = ["https://example.com/repo1", "https://example.com/repo2"]
            assert committee.invalid_urls == sorted(expected_invalid_urls)
            assert committee.related_urls == sorted(expected_related_urls)

    @mock.patch.dict("os.environ", {"SCRAPER_API_KEY": "test-token"})
    @mock.patch.object(Committee, "bulk_save", autospec=True)
    def test_handle_page_tree_none(self, mock_bulk_save, command, mock_committee):
        """Test handle when scraper page_tree is None - committee gets deactivated."""
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.page_tree = None

        mock_committees_list = [mock_committee]
        mock_active_committees = mock.MagicMock()
        mock_active_committees.__iter__.return_value = iter(mock_committees_list)
        mock_active_committees.count.return_value = 1
        mock_active_committees.__getitem__.return_value = mock_committees_list
        mock_active_committees.order_by.return_value = mock_active_committees

        with (
            mock.patch.object(Committee, "active_committees", mock_active_committees),
            mock.patch("builtins.print"),
            mock.patch("time.sleep"),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_committees.OwaspScraper",
                return_value=mock_scraper,
            ),
        ):
            command.handle(offset=0)

        mock_committee.deactivate.assert_called_once()

    @mock.patch.dict("os.environ", {"SCRAPER_API_KEY": "test-token"})
    @mock.patch.object(Committee, "bulk_save", autospec=True)
    def test_handle_no_leaders_emails(self, mock_bulk_save, command, mock_committee):
        """Test handle when committee has no leaders emails."""
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.page_tree = True

        mock_committee.get_leaders_emails.return_value = {}
        mock_committee.get_urls.return_value = []

        mock_committees_list = [mock_committee]
        mock_active_committees = mock.MagicMock()
        mock_active_committees.__iter__.return_value = iter(mock_committees_list)
        mock_active_committees.count.return_value = 1
        mock_active_committees.__getitem__.return_value = mock_committees_list
        mock_active_committees.order_by.return_value = mock_active_committees

        with (
            mock.patch.object(Committee, "active_committees", mock_active_committees),
            mock.patch("builtins.print"),
            mock.patch("time.sleep"),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_committees.OwaspScraper",
                return_value=mock_scraper,
            ),
        ):
            command.handle(offset=0)

        mock_committee.sync_leaders.assert_not_called()

    @mock.patch.dict("os.environ", {"SCRAPER_API_KEY": "test-token"})
    @mock.patch.object(Committee, "bulk_save", autospec=True)
    def test_handle_skipped_related_url(self, mock_bulk_save, command, mock_committee):
        """Test handle when get_related_url returns None for verified URL."""
        mock_scraper = mock.Mock(spec=OwaspScraper)
        mock_scraper.page_tree = True
        mock_scraper.verify_url.return_value = "https://example.com/verified"

        mock_committee.get_leaders_emails.return_value = {}
        mock_committee.get_urls.return_value = ["https://example.com/repo"]
        mock_committee.get_related_url.side_effect = [
            "https://example.com/repo",
            None,
        ]

        mock_committees_list = [mock_committee]
        mock_active_committees = mock.MagicMock()
        mock_active_committees.__iter__.return_value = iter(mock_committees_list)
        mock_active_committees.count.return_value = 1
        mock_active_committees.__getitem__.return_value = mock_committees_list
        mock_active_committees.order_by.return_value = mock_active_committees

        with (
            mock.patch.object(Committee, "active_committees", mock_active_committees),
            mock.patch("builtins.print"),
            mock.patch("time.sleep"),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_committees.OwaspScraper",
                return_value=mock_scraper,
            ),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_committees.normalize_url",
                side_effect=normalize_url,
            ),
        ):
            command.handle(offset=0)
