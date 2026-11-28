"""Verify checkpoint invariants against PostgreSQL, not mocked ORM calls."""

from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.core.utils.index import disable_indexing
from apps.github.models.repository import Repository
from apps.github.models.repository_contribution_sync_state import RepositoryContributionSyncState

pytestmark = pytest.mark.django_db


@pytest.fixture
def repository():
    now = timezone.now()
    with disable_indexing():
        yield Repository.objects.create(
            node_id="sync-state-test-repository",
            name="sync-state-test",
            key="sync-state-test",
            created_at=now,
            updated_at=now,
            pushed_at=now,
        )


def test_new_states_have_unknown_coverage(repository):
    for kind in RepositoryContributionSyncState.ContributionType:
        state = RepositoryContributionSyncState.objects.create(
            repository=repository, contribution_type=kind
        )
        state.refresh_from_db()
        assert state.covered_from is None
        assert state.covered_until is None
        assert state.last_attempt_at is None
        assert state.last_error == ""
        assert state.last_head_sha == ""
    assert repository.contribution_sync_states.count() == 3


def test_only_one_state_per_repository_and_type(repository):
    RepositoryContributionSyncState.objects.create(
        repository=repository, contribution_type="commits"
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        RepositoryContributionSyncState.objects.create(
            repository=repository, contribution_type="commits"
        )


@pytest.mark.parametrize(
    "invalid",
    [
        {"contribution_type": "unknown"},
        {"covered_from": "start"},
        {"covered_until": "end"},
        {"covered_from": "end", "covered_until": "start"},
        {"contribution_type": "issues", "default_branch": "main"},
        {"contribution_type": "pull_requests", "last_head_sha": "a" * 40},
        {"last_head_sha": "a" * 40},
        {"default_branch": "main", "last_head_sha": "a" * 40},
    ],
)
def test_invalid_checkpoint_is_rejected_by_database(repository, invalid):
    end = timezone.now()
    times = {"start": end - timedelta(days=365), "end": end}
    values = {key: times.get(value, value) for key, value in invalid.items()}
    with pytest.raises(IntegrityError), transaction.atomic():
        RepositoryContributionSyncState.objects.create(
            repository=repository, **{"contribution_type": "commits", **values}
        )


@pytest.mark.parametrize("kind", RepositoryContributionSyncState.ContributionType)
def test_completed_coverage_survives_a_failed_attempt(repository, kind):
    end = timezone.now()
    start = end - timedelta(days=365)
    metadata = {"default_branch": "main", "last_head_sha": "a" * 40} if kind == "commits" else {}
    state = RepositoryContributionSyncState.objects.create(
        repository=repository,
        contribution_type=kind,
        covered_from=start,
        covered_until=end,
        **metadata,
    )
    state.last_attempt_at = end + timedelta(days=1)
    state.last_error = "GitHub request failed (503)"
    state.save(update_fields=("last_attempt_at", "last_error", "nest_updated_at"))
    state.refresh_from_db()

    assert state.covered_from == start
    assert state.covered_until == end
    assert state.last_head_sha == metadata.get("last_head_sha", "")
    assert state.last_error == "GitHub request failed (503)"
    assert str(state).startswith("sync-state-test:")


def test_repository_deletion_removes_its_states(repository):
    state = RepositoryContributionSyncState.objects.create(
        repository=repository, contribution_type="commits"
    )
    repository.delete()
    assert not RepositoryContributionSyncState.objects.filter(pk=state.pk).exists()
