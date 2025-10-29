from unittest.mock import MagicMock

import pytest

from apps.owasp.management.commands.owasp_create_project_metadata_file import (
    MIN_PROJECT_TAGS,
    Command,
)
from apps.owasp.models.project import Project


@pytest.fixture
def mock_project():
    project = MagicMock(spec=Project)

    project.name = "Awesome Test Project"
    project.description = "A detailed pitch for an awesome test project."
    project.audience = ["builder", "defender"]
    project.type = "tool"
    project.level_raw = "3.5"
    project.owasp_url = "https://owasp.org/www-project-awesome/"

    leader1 = MagicMock()
    leader1.name = "Leader One"
    leader1.login = "leader1-github"
    leader1.email = "leader1@example.com"
    project.leaders.all.return_value = [leader1]

    repo1 = MagicMock()
    repo1.name = "main-repo"
    repo1.description = "The main source code repository."
    repo1.url = "https://github.com/owasp/main-repo"
    project.repositories.exists.return_value = True
    project.repositories.all.return_value = [repo1]

    project.licenses = ["MIT", "NOASSERTION", "Apache-2.0"]
    project.tags = ["security", "linter", "sast"]

    return project


class TestProjectMetadataCommand:
    def test_get_metadata_with_full_project_data(self, mock_project):
        command = Command()
        metadata = command.get_metadata(mock_project)

        assert metadata["name"] == "Awesome Test Project"
        assert metadata["pitch"] == "A detailed pitch for an awesome test project."
        assert metadata["audience"] == ["builder", "defender"]
        assert metadata["type"] == "tool"
        assert pytest.approx(metadata["level"]) == 3.5
        assert metadata["website"] == "https://owasp.org/www-project-awesome/"

        assert len(metadata["leaders"]) == 1
        assert metadata["leaders"][0] == {
            "name": "Leader One",
            "github": "leader1-github",
            "email": "leader1@example.com",
        }

        assert len(metadata["repositories"]) == 1
        assert metadata["repositories"][0] == {
            "name": "main-repo",
            "description": "The main source code repository.",
            "url": "https://github.com/owasp/main-repo",
        }

        assert metadata["license"] == ["MIT", "Apache-2.0"]
        assert metadata["tags"] == ["security", "linter", "sast"]

    def test_get_metadata_with_minimal_project_data(self, mock_project):
        command = Command()
        mock_project.owasp_url = None
        mock_project.licenses = []
        mock_project.tags = []
        mock_project.repositories.exists.return_value = False

        metadata = command.get_metadata(mock_project)

        for key in (
            "license",
            "repositories",
            "tags",
            "website",
        ):
            assert key not in metadata

        for key in (
            "level",
            "name",
            "pitch",
        ):
            assert key in metadata

    def test_get_metadata_license_filtering(self, mock_project):
        command = Command()
        mock_project.licenses = ["NOASSERTION"]

        metadata = command.get_metadata(mock_project)

        assert "license" not in metadata

    def test_get_metadata_tags_below_minimum(self, mock_project):
        command = Command()
        mock_project.tags = ["tag1"] * (MIN_PROJECT_TAGS - 1)

        metadata = command.get_metadata(mock_project)

        assert "tags" not in metadata

    def test_get_metadata_tags_at_minimum(self, mock_project):
        command = Command()
        mock_project.tags = ["tag1"] * MIN_PROJECT_TAGS

        metadata = command.get_metadata(mock_project)

        assert "tags" in metadata
        assert len(metadata["tags"]) == MIN_PROJECT_TAGS

    def test_get_metadata_with_partially_filled_related_objects(self, mock_project):
        command = Command()

        leader_partial = MagicMock()
        leader_partial.name = "Partial Leader"
        leader_partial.login = None
        leader_partial.email = "partial@example.com"
        mock_project.leaders.all.return_value = [leader_partial]

        repo_partial = MagicMock()
        repo_partial.name = "partial-repo"
        repo_partial.description = None
        repo_partial.url = "https://github.com/owasp/partial"
        mock_project.repositories.all.return_value = [repo_partial]

        metadata = command.get_metadata(mock_project)

        assert metadata["leaders"][0] == {"name": "Partial Leader", "email": "partial@example.com"}
        assert "github" not in metadata["leaders"][0]

        assert metadata["repositories"][0] == {
            "name": "partial-repo",
            "url": "https://github.com/owasp/partial",
        }
        assert "description" not in metadata["repositories"][0]
