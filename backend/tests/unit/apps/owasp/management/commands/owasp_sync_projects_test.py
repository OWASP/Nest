from argparse import ArgumentParser
from contextlib import nullcontext
from http import HTTPStatus
from unittest import mock

import pytest
import requests

from apps.owasp.management.commands.owasp_sync_projects import Command, Project


def project_record(**overrides):
    record = {
        "description": "<p>Know what's inside.</p>",
        "documentation_url": "https://cyclonedx.org",
        "github_url": "https://github.com/CycloneDX/cdxgen",
        "project_leaders": [{"contact": "ada@owasp.org", "name": "Ada Lovelace"}],
        "project_links": [{"title": "Site", "url": "https://cyclonedx.org"}],
        "project_type": "flagship",
        "slug": "cyclonedx",
        "status": "active",
        "tags": ["sbom"],
        "title": "CycloneDX",
        "website_url": "https://cyclonedx.org/",
    }
    record.update(overrides)
    return record


def use_real_adopt_key(project):
    """Run Project.adopt_key when the project under test is a mock."""
    project.adopt_key.side_effect = lambda key, existing=None: Project.adopt_key(
        project, key, existing
    )


def response(projects, *, status_code=HTTPStatus.OK):
    payload = mock.Mock()
    payload.status_code = status_code
    payload.headers = {}
    payload.json.return_value = {"projects": projects, "total": len(projects)}
    return payload


class TestOwaspSyncProjects:
    @pytest.fixture(autouse=True)
    def database_transaction(self, monkeypatch):
        """Keep these tests off the database while the command uses a transaction."""
        monkeypatch.setattr(
            "apps.owasp.management.commands.owasp_sync_projects.transaction.atomic",
            nullcontext,
        )

    @pytest.fixture
    def command(self):
        return Command()

    def test_add_arguments(self, command):
        """Test add_arguments adds expected arguments."""
        parser = ArgumentParser()
        command.add_arguments(parser)
        args = parser.parse_args([])
        assert args.offset == 0

    @pytest.fixture
    def mock_project(self):
        project = mock.Mock(spec=Project)
        project.id = 1
        project.key = "www-project-cyclonedx"
        project.name = "Old name"
        project.owasp_url = "https://owasp.org/www-project-cyclonedx"
        project.github_url = "https://github.com/owasp/www-project-cyclonedx"
        project.get_related_url.side_effect = lambda url, **_: url
        project.leaders_raw = ["Existing Leader"]
        project.is_active = True
        project.repositories.all.return_value = []
        project.repositories.exists.return_value = False
        use_real_adopt_key(project)
        return project

    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_updates_existing_project_without_renaming_key(
        self, mock_get, mock_bulk_save, command, mock_project
    ):
        """Test a www-project key is renamed to the website slug."""
        mock_get.return_value = response([project_record()])

        with mock.patch.object(Project, "objects") as mock_objects:
            mock_objects.prefetch_related.return_value = [mock_project]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        assert mock_project.key == "cyclonedx"
        assert mock_project.name == "CycloneDX"
        assert mock_project.description == "Know what's inside."
        assert mock_project.level == "flagship"
        assert mock_project.level_raw == 4
        assert mock_project.tags == ["sbom"]
        assert mock_project.is_active is True
        assert mock_project.leaders_raw == ["Ada Lovelace"]
        mock_project.sync_leaders.assert_called_once_with({"Ada Lovelace": "ada@owasp.org"})
        assert "https://github.com/CycloneDX/cdxgen" in mock_project.related_urls
        mock_project.deactivate.assert_not_called()
        assert mock_bulk_save.called

    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_preserves_leaders_when_source_has_none(
        self, mock_get, mock_bulk_save, command, mock_project
    ):
        """Test missing leaders on the website leave the stored leaders unchanged."""
        mock_get.return_value = response([project_record(project_leaders=[])])

        with mock.patch.object(Project, "objects") as mock_objects:
            mock_objects.prefetch_related.return_value = [mock_project]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        assert mock_project.leaders_raw == ["Existing Leader"]
        mock_project.sync_leaders.assert_not_called()

    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_stores_empty_level_raw_for_unknown_project_type(
        self, mock_get, mock_bulk_save, command, mock_project
    ):
        """Test an unknown project type does not store a non-numeric level_raw."""
        mock_get.return_value = response([project_record(project_type="archive")])

        with mock.patch.object(Project, "objects") as mock_objects:
            mock_objects.prefetch_related.return_value = [mock_project]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        assert mock_project.level == "other"
        assert mock_project.level_raw == ""

    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_creates_project_with_slug_key(self, mock_get, mock_bulk_save, command):
        """Test a project Nest has never seen is stored under the website slug."""
        mock_get.return_value = response([project_record(project_leaders=None)])

        with (
            mock.patch.object(Project, "objects") as mock_objects,
            mock.patch.object(Project, "sync_leaders"),
        ):
            mock_objects.prefetch_related.return_value = []
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        created = mock_bulk_save.call_args_list[0].args[0][0]
        assert created.key == "cyclonedx"
        assert created.name == "CycloneDX"

    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_deactivates_project_missing_from_catalog(
        self, mock_get, mock_bulk_save, command, mock_project
    ):
        """Test an active local project absent from a complete catalog is deactivated."""
        mock_get.return_value = response([project_record()])
        stale = mock.Mock(spec=Project)
        stale.id = 2
        stale.key = "www-project-retired"
        stale.is_active = True
        stale.repositories.all.return_value = []

        with mock.patch.object(Project, "objects") as mock_objects:
            mock_objects.prefetch_related.return_value = [mock_project, stale]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        stale.deactivate.assert_called_once()
        mock_project.deactivate.assert_not_called()

    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_leaves_projects_unchanged_when_fetch_fails(
        self, mock_get, mock_bulk_save, command, mock_project
    ):
        """Test a failed catalog request does not write or deactivate projects."""
        mock_get.side_effect = requests.exceptions.RequestException("offline")

        with mock.patch.object(Project, "objects") as mock_objects:
            mock_objects.prefetch_related.return_value = [mock_project]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        mock_bulk_save.assert_not_called()
        mock_project.deactivate.assert_not_called()
        mock_project.sync_leaders.assert_not_called()
        assert mock_project.leaders_raw == ["Existing Leader"]

    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_leaves_projects_unchanged_when_a_row_has_no_slug(
        self, mock_get, mock_bulk_save, command, mock_project
    ):
        """Test a blank slug aborts reconciliation even when other rows are valid."""
        mock_get.return_value = response([project_record(), project_record(slug="")])
        stale = mock.Mock(spec=Project)
        stale.id = 2
        stale.key = "www-project-retired"
        stale.is_active = True
        stale.repositories.all.return_value = []

        with mock.patch.object(Project, "objects") as mock_objects:
            mock_objects.prefetch_related.return_value = [mock_project, stale]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        mock_bulk_save.assert_not_called()
        mock_project.deactivate.assert_not_called()
        stale.deactivate.assert_not_called()

    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_skips_deactivation_when_offset_is_set(
        self, mock_get, mock_bulk_save, command, mock_project
    ):
        """Test a partial run updates from the offset without reconciling absences."""
        mock_get.return_value = response([project_record(slug="other"), project_record()])
        stale = mock.Mock(spec=Project)
        stale.id = 2
        stale.key = "www-project-retired"
        stale.is_active = True
        stale.repositories.all.return_value = []

        with mock.patch.object(Project, "objects") as mock_objects:
            mock_objects.prefetch_related.return_value = [mock_project, stale]
            command.stdout = mock.MagicMock()
            command.handle(offset=1)

        assert mock_bulk_save.called
        assert mock_project.key == "cyclonedx"
        command.stdout.write.assert_called_once_with("2 of 2 cyclonedx\n")
        stale.deactivate.assert_not_called()
        mock_project.deactivate.assert_not_called()

    @mock.patch.object(Project, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_reuses_the_slug_stub_instead_of_deleting_it(self, mock_get, mock_bulk_save, command):
        """Test a repositoryless slug row receives the matched project's repositories."""
        repository = mock.Mock()
        repository.key = "CheatSheetSeries"
        project = mock.Mock(spec=Project)
        project.id = 1
        project.pk = 1
        project.key = "www-project-cheat-sheets"
        project.name = "OWASP Cheat Sheet Series"
        project.github_url = "https://github.com/owasp/www-project-cheat-sheets"
        project.owasp_url = "https://owasp.org/www-project-cheat-sheets"
        project.owasp_repository_id = 9
        project.get_related_url.side_effect = lambda url, **_: url
        project.leaders_raw = ["Jim Manico"]
        project.is_active = True
        project.repositories.all.return_value = [repository]
        project.repositories.exists.return_value = True
        use_real_adopt_key(project)

        stub = mock.Mock(spec=Project)
        stub.id = 2
        stub.pk = 2
        stub.key = "cheat-sheet-series"
        stub.name = "Stub"
        stub.github_url = ""
        stub.owasp_url = "https://owasp.org/projects/cheat-sheet-series"
        stub.owasp_repository_id = None
        stub.get_related_url.side_effect = lambda url, **_: url
        stub.leaders_raw = []
        stub.is_active = True
        stub.repositories.all.return_value = []
        stub.repositories.exists.return_value = False

        mock_get.return_value = response(
            [
                project_record(
                    github_url="https://github.com/OWASP/CheatSheetSeries",
                    project_url="https://owasp.org/www-project-cheat-sheets/",
                    slug="cheat-sheet-series",
                    title="OWASP Cheat Sheet Series",
                )
            ]
        )

        with mock.patch.object(Project, "objects") as mock_objects:
            mock_objects.prefetch_related.return_value = [project, stub]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        stub.delete.assert_not_called()
        stub.repositories.add.assert_called_once_with(repository)
        project.repositories.clear.assert_called_once()
        project.deactivate.assert_not_called()
        project.save.assert_called_once_with(update_fields=["is_active", "owasp_repository"])
        assert project.is_active is False
        assert project.owasp_repository_id is None
        assert stub.key == "cheat-sheet-series"
        assert stub.name == "OWASP Cheat Sheet Series"
        assert stub.owasp_repository_id == 9
        assert mock_bulk_save.called
