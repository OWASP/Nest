from unittest.mock import patch, Mock
import pytest
from django.utils.timezone import now, timedelta
from apps.owasp.models.snapshot import Snapshot


class TestSnapshotModel:
    @pytest.mark.parametrize(
        ("start_at", "end_at", "status", "expected_str"),
        [
            (now(), now() + timedelta(days=1), Snapshot.Status.PENDING, "Snapshot"),
            (now(), now(), Snapshot.Status.COMPLETED, "Snapshot"),
        ],
    )
    def test_str_representation(self, start_at, end_at, status, expected_str):
        snapshot = Snapshot(start_at=start_at, end_at=end_at, status=status)
        assert expected_str in str(snapshot)

    def test_default_status(self):
        snapshot = Snapshot()
        assert snapshot.status == Snapshot.Status.PENDING

    @pytest.mark.parametrize("status", Snapshot.Status.values)
    def test_status_choices(self, status):
        snapshot = Snapshot(status=status)
        assert snapshot.status == status

    def test_save_method(self):
        snapshot = Snapshot()
        with patch("apps.owasp.models.snapshot.BulkSaveModel.save") as mock_save:
            snapshot.save()
        mock_save.assert_called_once()

    def test_fetch_pending_snapshots(self):
        with patch("apps.owasp.models.snapshot.Snapshot.objects.filter") as mock_filter:
            Snapshot.objects.filter(status=Snapshot.Status.PENDING)
            mock_filter.assert_called_once_with(status=Snapshot.Status.PENDING)

    def test_snapshot_processing(self):
        snapshot = Snapshot(status=Snapshot.Status.PENDING)
        snapshot.status = Snapshot.Status.PROCESSING
        assert snapshot.status == Snapshot.Status.PROCESSING

    def test_snapshot_completion(self):
        snapshot = Snapshot(status=Snapshot.Status.PROCESSING)
        snapshot.status = Snapshot.Status.COMPLETED
        assert snapshot.status == Snapshot.Status.COMPLETED
