import pytest

from apps.owasp.models.snapshot import Snapshot


class TestSnapshotModel:
    @pytest.mark.parametrize(
        ("start_at", "end_at", "status", "expected_str"),
        [
            (
                "2024-02-10 10:00:00",
                "2024-02-10 12:00:00",
                "pending",
                "Snapshot 2024-02-10 10:00:00 to 2024-02-10 12:00:00 (pending)",
            ),
            (
                "2024-02-11 14:00:00",
                "2024-02-11 16:00:00",
                "completed",
                "Snapshot 2024-02-11 14:00:00 to 2024-02-11 16:00:00 (completed)",
            ),
        ],
    )
    def test_str_representation(self, start_at, end_at, status, expected_str):
        snapshot = Snapshot(start_at=start_at, end_at=end_at, status=status)
        assert str(snapshot) == expected_str

    def test_default_status(self):
        """Ensure that default status is 'pending'."""
        snapshot = Snapshot()
        assert snapshot.status == Snapshot.Status.PENDING

    def test_ordering(self):
        """Ensure that snapshots are ordered by '-start_at'."""
        assert Snapshot._meta.ordering == ["-start_at"]

    def test_indexes(self):
        """Check if indexes are correctly set."""
        index_fields = [list(index.fields) for index in Snapshot._meta.indexes]
        assert ["status"] in index_fields
        assert ["start_at", "end_at"] in index_fields
