import json
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from apps.owasp.management.commands.add_project_custom_tags import Command, Project


class TestAddProjectCustomTags:
    @pytest.mark.parametrize(
        ("file_exists", "file_content", "expected_output"),
        [
            (False, None, "File not found: /mocked/path/data/project-custom-tags/test-file.json"),
            (
                True,
                json.dumps({"projects": [], "tags": []}),
                "No projects or tags found in the file.",
            ),
            (
                True,
                json.dumps({"projects": ["proj1"], "tags": ["tag1"]}),
                "Project proj1 does not exists.",
            ),
        ],
    )
    @patch("apps.owasp.management.commands.add_project_custom_tags.Project.objects.get")
    @patch("apps.owasp.management.commands.add_project_custom_tags.Path.open")
    @patch("apps.owasp.management.commands.add_project_custom_tags.Path.exists")
    @patch(
        "apps.owasp.management.commands.add_project_custom_tags.settings.BASE_DIR",
        new=Path("/mocked/path"),
    )
    def test_handle(
        self,
        mock_exists,
        mock_open_func,
        mock_get,
        file_exists,
        file_content,
        expected_output,
        capsys,
    ):
        mock_exists.return_value = file_exists
        mock_open_func.side_effect = (
            lambda *_args, **__kwargs: StringIO(file_content) if file_content else None
        )

        def mock_get_side_effect(key):
            if key == "proj1":
                raise Project.DoesNotExist
            mock_project = MagicMock()
            mock_project.custom_tags = []
            return mock_project

        mock_get.side_effect = mock_get_side_effect
        command = Command()

        command.handle(**{"file-name": "test-file.json"})

        captured = capsys.readouterr()
        assert expected_output in captured.err

    @pytest.mark.parametrize(
        ("file_content", "projects", "expected_saved_tags"),
        [
            (
                json.dumps({"projects": ["proj1"], "tags": ["tag1"]}),
                {"proj1": ["tag2"]},
                {"proj1": ["tag1", "tag2"]},
            ),
        ],
    )
    @patch("apps.owasp.management.commands.add_project_custom_tags.Project.objects.get")
    @patch("apps.owasp.management.commands.add_project_custom_tags.Path.open")
    @patch("apps.owasp.management.commands.add_project_custom_tags.Path.exists")
    @patch(
        "apps.owasp.management.commands.add_project_custom_tags.settings.BASE_DIR",
        new=Path("/mocked/path"),
    )
    def test_handle_with_projects_and_tags(
        self,
        mock_exists,
        mock_open_func,
        mock_get,
        file_content,
        projects,
        expected_saved_tags,
    ):
        mock_exists.return_value = True
        mock_open_func.side_effect = lambda *_args, **__kwargs: StringIO(file_content)

        class MockProject:
            def __init__(self, key):
                self.key = key
                self.custom_tags = projects[key]

            def save(self):
                projects[self.key] = self.custom_tags

        mock_get.side_effect = lambda key: MockProject(key)
        command = Command()

        command.handle(**{"file-name": "test-file.json"})

        for key, expected_tags in expected_saved_tags.items():
            assert sorted(projects[key]) == sorted(expected_tags)
