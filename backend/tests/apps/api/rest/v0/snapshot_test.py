from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory

from apps.api.rest.v0.snapshot import (
    SnapshotDetail,
    get_snapshot,
    list_snapshot_chapters,
    list_snapshot_issues,
    list_snapshot_members,
    list_snapshot_projects,
    list_snapshot_releases,
    list_snapshots,
)
from apps.github.models.issue import Issue
from apps.github.models.release import Release
from apps.github.models.user import User
from apps.owasp.models import Chapter, Project
from apps.owasp.models.snapshot import Snapshot as SnapshotModel


class TestSnapshotSchema:
    @pytest.mark.parametrize(
        "snapshot_data",
        [
            {
                "created_at": "2025-02-01T00:00:00Z",
                "end_at": "2025-02-28T23:59:59Z",
                "key": "2025-02",
                "start_at": "2025-02-01T00:00:00Z",
                "title": "February 2025 Snapshot",
                "updated_at": "2025-03-01T00:00:00Z",
                "new_chapters_count": 1,
                "new_issues_count": 2,
                "new_projects_count": 3,
                "new_releases_count": 4,
                "new_users_count": 5,
            },
            {
                "created_at": "2024-01-01T00:00:00Z",
                "end_at": "2024-01-31T23:59:59Z",
                "key": "2024-01",
                "start_at": "2024-01-01T00:00:00Z",
                "title": "January 2024 Snapshot",
                "updated_at": "2024-02-01T00:00:00Z",
                "new_chapters_count": 0,
                "new_issues_count": 0,
                "new_projects_count": 0,
                "new_releases_count": 0,
                "new_users_count": 0,
            },
        ],
    )
    def test_snapshot_detail_schema(self, snapshot_data):
        snapshot = SnapshotDetail(**snapshot_data)

        assert snapshot.created_at == datetime.fromisoformat(snapshot_data["created_at"])
        assert snapshot.end_at == datetime.fromisoformat(snapshot_data["end_at"])
        assert snapshot.key == snapshot_data["key"]
        assert snapshot.start_at == datetime.fromisoformat(snapshot_data["start_at"])
        assert snapshot.title == snapshot_data["title"]
        assert snapshot.updated_at == datetime.fromisoformat(snapshot_data["updated_at"])
        assert snapshot.new_chapters_count == snapshot_data["new_chapters_count"]
        assert snapshot.new_issues_count == snapshot_data["new_issues_count"]
        assert snapshot.new_projects_count == snapshot_data["new_projects_count"]
        assert snapshot.new_releases_count == snapshot_data["new_releases_count"]
        assert snapshot.new_users_count == snapshot_data["new_users_count"]


class TestSnapshotAPI:
    def setup_method(self):
        self.factory = RequestFactory()

        self.snapshot = MagicMock(spec=SnapshotModel)
        self.snapshot.key = "2025-02"
        self.snapshot.title = "February 2025 Snapshot"
        self.snapshot.status = SnapshotModel.Status.COMPLETED
        self.snapshot.start_at = "2025-02-01T00:00:00Z"
        self.snapshot.end_at = "2025-02-28T23:59:59Z"
        self.chapter = MagicMock(spec=Chapter)
        self.chapter.name = "Test Chapter"
        self.issue = MagicMock(spec=Issue)
        self.issue.title = "Test Issue"
        self.project = MagicMock(spec=Project)
        self.project.name = "Test Project"
        self.release = MagicMock(spec=Release)
        self.release.tag_name = "v1.0.0"
        self.user = MagicMock(spec=User)
        self.user.username = "testuser"
        self.snapshot.new_chapters.order_by.return_value = [self.chapter]
        self.snapshot.new_issues.select_related.return_value.order_by.return_value = [self.issue]
        self.snapshot.new_projects.order_by.return_value = [self.project]
        self.snapshot.new_releases.select_related.return_value.order_by.return_value = [
            self.release
        ]
        self.snapshot.new_users.order_by.return_value = [self.user]

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_get_snapshot_not_found(self, mock_filter):
        mock_filter.return_value.first.return_value = None
        request = self.factory.get("")

        response = get_snapshot(request, snapshot_id="non-existent")

        assert response.status_code == HTTPStatus.NOT_FOUND

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_get_snapshot_success(self, mock_filter):
        mock_filter.return_value.first.return_value = self.snapshot
        request = self.factory.get("")

        response = get_snapshot(request, snapshot_id=self.snapshot.key)

        assert response.key == self.snapshot.key
        assert response.title == self.snapshot.title
        assert response.start_at == self.snapshot.start_at
        assert response.end_at == self.snapshot.end_at

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_chapters_not_found(self, mock_filter):
        mock_filter.return_value.first.return_value = None
        request = self.factory.get("")

        response = list_snapshot_chapters(request, snapshot_id="non-existent")

        assert len(response) == 0

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_chapters_success(self, mock_filter):
        mock_filter.return_value.first.return_value = self.snapshot
        request = self.factory.get("")

        response = list_snapshot_chapters(request, snapshot_id=self.snapshot.key)

        assert len(response) == 1
        assert response[0] == self.chapter
        assert response[0].name == self.chapter.name

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_issues_no_repository(self, mock_filter):
        self.issue.repository = None
        mock_filter.return_value.first.return_value = self.snapshot
        request = self.factory.get("")

        response = list_snapshot_issues(request, snapshot_id=self.snapshot.key)

        assert len(response) == 1
        assert response[0] == self.issue

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_issues_not_found(self, mock_filter):
        mock_filter.return_value.first.return_value = None
        request = self.factory.get("")

        response = list_snapshot_issues(request, snapshot_id="non-existent")

        assert len(response) == 0

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_issues_success(self, mock_filter):
        mock_filter.return_value.first.return_value = self.snapshot
        request = self.factory.get("")

        response = list_snapshot_issues(request, snapshot_id=self.snapshot.key)

        assert len(response) == 1
        assert response[0] == self.issue
        assert response[0].title == self.issue.title

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_members_not_found(self, mock_filter):
        mock_filter.return_value.first.return_value = None
        request = self.factory.get("")

        response = list_snapshot_members(request, snapshot_id="non-existent")

        assert len(response) == 0

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_members_success(self, mock_filter):
        mock_filter.return_value.first.return_value = self.snapshot
        request = self.factory.get("")

        response = list_snapshot_members(request, snapshot_id=self.snapshot.key)

        assert len(response) == 1
        assert response[0] == self.user
        assert response[0].username == self.user.username

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_projects_not_found(self, mock_filter):
        mock_filter.return_value.first.return_value = None
        request = self.factory.get("")

        response = list_snapshot_projects(request, snapshot_id="non-existent")

        assert len(response) == 0

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_projects_success(self, mock_filter):
        mock_filter.return_value.first.return_value = self.snapshot
        request = self.factory.get("")

        response = list_snapshot_projects(request, snapshot_id=self.snapshot.key)

        assert len(response) == 1
        assert response[0] == self.project
        assert response[0].name == self.project.name

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_releases_no_repository(self, mock_filter):
        self.release.repository = None
        mock_filter.return_value.first.return_value = self.snapshot
        request = self.factory.get("")

        response = list_snapshot_releases(request, snapshot_id=self.snapshot.key)

        assert len(response) == 1
        assert response[0] == self.release

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_releases_not_found(self, mock_filter):
        mock_filter.return_value.first.return_value = None
        request = self.factory.get("")

        response = list_snapshot_releases(request, snapshot_id="non-existent")

        assert len(response) == 0

    @patch("apps.owasp.models.snapshot.Snapshot.objects.filter")
    def test_list_snapshot_releases_success(self, mock_filter):
        mock_filter.return_value.first.return_value = self.snapshot
        request = self.factory.get("")

        response = list_snapshot_releases(request, snapshot_id=self.snapshot.key)

        assert len(response) == 1
        assert response[0] == self.release
        assert response[0].tag_name == self.release.tag_name

    def test_snapshot_issue_resolver_no_organization(self):
        from apps.api.rest.v0.snapshot import SnapshotIssue

        issue = MagicMock(spec=Issue)
        issue.repository = MagicMock()
        issue.repository.organization = None
        issue.repository.name = "test-repo"

        assert SnapshotIssue.resolve_organization_login(issue) is None
        assert SnapshotIssue.resolve_repository_name(issue) == "test-repo"

    def test_snapshot_release_resolver_no_organization(self):
        from apps.api.rest.v0.snapshot import SnapshotRelease

        release = MagicMock(spec=Release)
        release.repository = MagicMock()
        release.repository.organization = None
        release.repository.name = "test-repo"

        assert SnapshotRelease.resolve_organization_login(release) is None
        assert SnapshotRelease.resolve_repository_name(release) == "test-repo"


class TestListSnapshots:
    """Tests for list_snapshots endpoint."""

    @patch("apps.api.rest.v0.snapshot.SnapshotModel")
    def test_list_snapshots_default_ordering(self, mock_snapshot_model):
        """Test listing snapshots with default ordering."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()
        mock_snapshot_model.objects.filter.return_value.order_by.return_value = mock_queryset

        result = list_snapshots(mock_request, ordering=None)

        mock_snapshot_model.objects.filter.assert_called_with(
            status=mock_snapshot_model.Status.COMPLETED
        )
        mock_snapshot_model.objects.filter.return_value.order_by.assert_called_with("-created_at")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.snapshot.SnapshotModel")
    def test_list_snapshots_with_ordering(self, mock_snapshot_model):
        """Test listing snapshots with custom ordering."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()
        mock_snapshot_model.objects.filter.return_value.order_by.return_value = mock_queryset

        result = list_snapshots(mock_request, ordering="start_at")

        mock_snapshot_model.objects.filter.return_value.order_by.assert_called_with("start_at")
        assert result == mock_queryset
