from argparse import ArgumentParser
from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_enrich_committees import (
    Command,
    Committee,
    Prompt,
)


class TestOwaspEnrichCommittees:
    @pytest.fixture
    def command(self):
        return Command()

    def test_add_arguments(self, command):
        """Test add_arguments adds expected arguments."""
        parser = ArgumentParser()
        command.add_arguments(parser)
        args = parser.parse_args([])
        assert args.offset == 0
        assert not args.force_update_summary
        assert args.update_summary

    @pytest.fixture
    def mock_committee(self):
        committee = mock.Mock(spec=Committee)
        committee.owasp_url = "https://owasp.org/www-committee-test"
        committee.summary = None
        return committee

    @pytest.mark.parametrize(
        ("offset", "committees", "force_update_summary", "update_summary"),
        [
            (0, 3, False, True),
            (2, 5, True, True),
            (0, 6, False, False),
            (1, 8, True, False),
        ],
    )
    @mock.patch.dict("os.environ", {"OPENAI_API_KEY": "test-token"})
    @mock.patch.object(Committee, "bulk_save", autospec=True)
    def test_handle(
        self,
        mock_bulk_save,
        command,
        mock_committee,
        offset,
        committees,
        force_update_summary,
        update_summary,
    ):
        mock_prompt = mock.Mock()
        mock_prompt.get_owasp_committee_summary.return_value = "summary prompt"

        mock_committee.generate_summary.side_effect = lambda *_args, **__kwargs: setattr(
            mock_committee, "summary", "Generated summary"
        )

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

        mock_active_committees_without_summary = mock.MagicMock()
        mock_active_committees_without_summary.__iter__.return_value = iter(mock_committees_list)
        mock_active_committees_without_summary.count.return_value = len(mock_committees_list)
        mock_active_committees_without_summary.__getitem__.side_effect = lambda idx: (
            mock_committees_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_committees_list[idx]
        )
        mock_active_committees_without_summary.order_by.return_value = (
            mock_active_committees_without_summary
        )

        with (
            mock.patch.object(Committee, "active_committees", mock_active_committees),
            mock.patch.object(
                Committee.active_committees,
                "without_summary",
                mock_active_committees_without_summary,
            ),
            mock.patch.object(
                Prompt, "get_owasp_committee_summary", mock_prompt.get_owasp_committee_summary
            ),
        ):
            command.stdout = mock.MagicMock()
            command.handle(
                offset=offset,
                force_update_summary=force_update_summary,
                update_summary=update_summary,
            )

        if force_update_summary:
            mock_active_committees.count.assert_called_once()
        else:
            mock_active_committees_without_summary.count.assert_called_once()

        mock_bulk_save.assert_called()

        assert command.stdout.write.call_count == committees - offset

        for call in command.stdout.write.call_args_list:
            args = call[0]
            assert "https://owasp.org/www-committee-test" in args[0]

        if update_summary:
            for committee in mock_committees_list:
                assert committee.summary == "Generated summary"
        else:
            for committee in mock_committees_list:
                assert committee.summary is None
