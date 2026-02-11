from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_enrich_projects import (
    Command,
    Project,
    Prompt,
)


class TestOwaspEnrichProjects:
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
        assert args.force_update_summary is False
        assert args.update_summary is True

    @pytest.fixture
    def mock_project(self):
        project = mock.Mock(spec=Project)
        project.owasp_url = "https://owasp.org/www-project-test"
        project.summary = None
        return project

    @pytest.mark.parametrize(
        ("offset", "projects", "force_update_summary", "update_summary"),
        [
            (0, 3, False, True),
            (2, 5, True, True),
            (0, 6, False, False),
            (1, 8, True, False),
        ],
    )
    @mock.patch.dict("os.environ", {"OPENAI_API_KEY": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    def test_handle(
        self,
        mock_bulk_save,
        command,
        mock_project,
        offset,
        projects,
        force_update_summary,
        update_summary,
    ):
        mock_prompt = mock.Mock()
        mock_prompt.get_owasp_project_summary.return_value = "summary prompt"

        mock_project.generate_summary.side_effect = lambda *_args, **__kwargs: setattr(
            mock_project, "summary", "Generated summary"
        )

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

        mock_active_projects_without_summary = mock.MagicMock()
        mock_active_projects_without_summary.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects_without_summary.count.return_value = len(mock_projects_list)
        mock_active_projects_without_summary.__getitem__.side_effect = lambda idx: (
            mock_projects_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_projects_list[idx]
        )
        mock_active_projects_without_summary.order_by.return_value = (
            mock_active_projects_without_summary
        )

        with (
            mock.patch.object(Project, "active_projects", mock_active_projects),
            mock.patch.object(
                Project.active_projects, "without_summary", mock_active_projects_without_summary
            ),
            mock.patch.object(
                Prompt, "get_owasp_project_summary", mock_prompt.get_owasp_project_summary
            ),
            mock.patch("builtins.print") as mock_print,
        ):
            command.handle(
                offset=offset,
                force_update_summary=force_update_summary,
                update_summary=update_summary,
            )

        if force_update_summary:
            mock_active_projects.count.assert_called_once()
        else:
            mock_active_projects_without_summary.count.assert_called_once()

        assert mock_bulk_save.called

        assert mock_print.call_count == projects - offset

        for call in mock_print.call_args_list:
            args, _ = call
            assert "https://owasp.org/www-project-test" in args[0]

        if update_summary:
            for project in mock_projects_list:
                assert project.summary == "Generated summary"
        else:
            for project in mock_projects_list:
                assert project.summary is None
