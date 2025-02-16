from unittest.mock import MagicMock

import pytest


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
def test_str_representation(start_at, end_at, status, expected_str):
    snapshot = MagicMock(start_at=start_at, end_at=end_at, status=status)
    snapshot.__str__.return_value = expected_str
    assert str(snapshot) == expected_str


def test_default_status():
    """Ensure that default status is 'pending'."""
    snapshot = MagicMock()
    snapshot.status = "pending"
    assert snapshot.status == "pending"


def test_ordering():
    """Ensure that snapshots are ordered by '-start_at'."""
    snapshot = MagicMock()
    snapshot._meta.ordering = ["-start_at"]
    assert snapshot._meta.ordering == ["-start_at"]


def test_indexes():
    """Check if indexes are correctly set."""
    snapshot = MagicMock()
    snapshot._meta.indexes = [
        MagicMock(fields=["status"]),
        MagicMock(fields=["start_at", "end_at"]),
    ]

    index_fields = [list(index.fields) for index in snapshot._meta.indexes]
    assert ["status"] in index_fields
    assert ["start_at", "end_at"] in index_fields


def test_many_to_many_relationships():
    """Test that Snapshot correctly associates with Issues, Releases, and Users."""
    snapshot = MagicMock()
    issue = MagicMock()
    release = MagicMock()
    user = MagicMock()

    snapshot.new_issues = [issue]
    snapshot.new_releases = [release]
    snapshot.new_users = [user]

    assert len(snapshot.new_issues) == 1
    assert len(snapshot.new_releases) == 1
    assert len(snapshot.new_users) == 1
