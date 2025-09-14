import os
from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_scrape_committees import (
    Command,
    Committee,
    normalize_url,
)


class TestOwaspScrapeCommittees:
    @pytest.fixture
    def command(self):
        return Command()

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
    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Committee, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.management.commands.owasp_scrape_committees.get_github_client")
    def test_handle(
        self, mock_github, mock_bulk_save, command, mock_committee, offset, committees
    ):
        mock_committee.get_urls.return_value = [
            "https://example.com/repo1",
            "https://example.com/repo2",
            "https://invalid.com/repo3",
        ]
        mock_committee.verify_url.side_effect = lambda url: None if "invalid" in url else url
        mock_committee.get_related_url.side_effect = lambda url, **_: url

        mock_committees_list = [mock_committee] * committees

        mock_active_committees = mock.MagicMock()
        mock_active_committees.__iter__.return_value = iter(mock_committees_list)
        mock_active_committees.count.return_value = len(mock_committees_list)
        mock_active_committees.__getitem__.side_effect = (
            lambda idx: mock_committees_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_committees_list[idx]
        )
        mock_active_committees.order_by.return_value = mock_active_committees

        mock_github_instance = mock.Mock()
        mock_github.return_value = mock_github_instance
        mock_github_instance.get_repo.return_value = mock.Mock()

        with (
            mock.patch.object(Committee, "active_committees", mock_active_committees),
            mock.patch("builtins.print") as mock_print,
            mock.patch("time.sleep", return_value=None),
            mock.patch(
                "apps.owasp.management.commands.owasp_scrape_committees.normalize_url",
                side_effect=normalize_url,
            ),
        ):
            command.handle(offset=offset)

        mock_active_committees.count.assert_called_once()

        assert mock_bulk_save.called

        assert mock_print.call_count == (committees - offset)

        for call in mock_print.call_args_list:
            args, _ = call
            assert "https://owasp.org/www-committee-test" in args[0]

        for committee in mock_committees_list:
            expected_invalid_urls = ["https://invalid.com/repo3"]
            expected_related_urls = ["https://example.com/repo1", "https://example.com/repo2"]
            assert committee.invalid_urls == sorted(expected_invalid_urls)
            assert committee.related_urls == sorted(expected_related_urls)
