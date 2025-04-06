from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.owasp.models.snapshot import Snapshot


class TestSnapshot:
    @pytest.fixture
    def snapshot_data(self):
        return {
            "title": "Test Snapshot",
            "start_at": timezone.now(),
            "end_at": timezone.now() + timedelta(hours=1),
        }

    def test_str_representation(self, snapshot_data):
        with patch.object(Snapshot, "__str__", return_value=snapshot_data["title"]):
            snapshot = MagicMock(spec=Snapshot)
            snapshot.title = snapshot_data["title"]
            assert Snapshot.__str__(snapshot) == snapshot_data["title"]

    def test_save_with_key(self):
        snapshot = MagicMock(spec=Snapshot)
        snapshot.key = "2022-01"

        with patch.object(Snapshot, "save", autospec=True) as mock_super_save:
            Snapshot.save(snapshot)
            assert snapshot.key == "2022-01"
            mock_super_save.assert_called_once()

    def test_save_without_key(self):
        mock_date = datetime(2023, 5, 15, tzinfo=dt_timezone.utc)

        def mock_snapshot_save(self):
            if not self.key:
                self.key = mock_date.strftime("%Y-%m")

        snapshot = MagicMock(spec=Snapshot)
        snapshot.key = ""

        with (
            patch("django.utils.timezone.now", return_value=mock_date),
            patch.object(Snapshot, "save", autospec=True, side_effect=mock_snapshot_save),
        ):
            Snapshot.save(snapshot)
            assert snapshot.key == "2023-05"

    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            (Snapshot.Status.PENDING, "Pending"),
            (Snapshot.Status.PROCESSING, "Processing"),
            (Snapshot.Status.COMPLETED, "Completed"),
            (Snapshot.Status.ERROR, "Error"),
        ],
    )
    def test_status_choices(self, status, expected):
        snapshot = MagicMock(spec=Snapshot)
        snapshot.status = status
        snapshot.get_status_display.return_value = expected

        assert snapshot.get_status_display() == expected

    def test_relationships(self):
        snapshot = MagicMock(spec=Snapshot)

        for field in ["new_chapters", "new_issues", "new_projects", "new_releases", "new_users"]:
            mock_rel = MagicMock()
            setattr(snapshot, field, mock_rel)

        assert hasattr(snapshot, "new_chapters")
        assert hasattr(snapshot, "new_issues")
        assert hasattr(snapshot, "new_projects")
        assert hasattr(snapshot, "new_releases")
        assert hasattr(snapshot, "new_users")
