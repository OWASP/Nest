"""Exercise repository contribution ingestion with real persistence and aggregation."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import UTC, datetime, timedelta
from threading import Event
from types import SimpleNamespace
from unittest.mock import Mock, PropertyMock

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import DatabaseError, IntegrityError, close_old_connections, connection
from github.Comparison import Comparison
from github.GithubException import GithubException, UnknownObjectException

from apps.core.utils.index import disable_indexing
from apps.github import common
from apps.github.common import sync_repository
from apps.github.management.commands.github_sync_contributions import Command as RepairCommand
from apps.github.management.commands.github_update_owasp_organization import Command as SyncCommand
from apps.github.models.commit import Commit
from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.github.models.repository import Repository
from apps.github.models.repository_contribution_sync_state import RepositoryContributionSyncState
from apps.github.models.user import User
from apps.owasp.management.commands.owasp_aggregate_entity_contributions import Command
from apps.owasp.management.commands.owasp_aggregate_member_contributions import (
    Command as MemberCommand,
)
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.member_snapshot import MemberSnapshot
from apps.owasp.models.project import Project
from apps.slack.models.conversation import Conversation
from apps.slack.models.message import Message
from apps.slack.models.workspace import Workspace

pytestmark = pytest.mark.django_db
END = datetime(2026, 11, 3, 12, tzinfo=UTC)
START = END - timedelta(days=365)


def github_commit(key, *, date=None, author=None, committer=None):
    return SimpleNamespace(
        raw_data={"node_id": f"commit-{key}"},
        node_id=f"commit-{key}",
        sha=key * 40,
        commit=SimpleNamespace(
            message=f"Commit {key}", author=SimpleNamespace(date=date or END - timedelta(days=180))
        ),
        author=author,
        committer=committer,
    )


@pytest.fixture
def source(mocker):
    mocker.patch("apps.github.common.timezone.now", return_value=END)
    with disable_indexing():
        repository = Repository.objects.create(
            node_id="commit-sync-repository",
            key="commit-sync-test",
            name="commit-sync-test",
            default_branch="main",
            created_at=START,
            updated_at=END,
            pushed_at=END,
        )
        mocker.patch("apps.github.common.Repository.update_data", return_value=repository)
        remote = Mock()
        remote.name = repository.name
        remote.default_branch = "main"
        remote.compare.return_value.status = "diverged"
        remote.organization = None
        remote.get_branch.return_value.commit.sha = "f" * 40
        for name in ("contributors", "milestones", "issues", "pulls", "releases", "commits"):
            getattr(remote, f"get_{name}").return_value = []
        remote.get_languages.return_value = {}
        # Supplying an owner avoids unrelated owner-profile synchronization in these tests.
        yield remote, repository


def run_sync(remote, repository):
    return sync_repository(remote, user=repository.owner or Mock())


def test_normal_sync_populates_commit_activity(source):
    remote, repository = source
    commit = github_commit("a")
    remote.get_commits.return_value = [commit]
    run_sync(remote, repository)

    assert Commit.objects.filter(repository=repository, sha=commit.sha).count() == 1
    stored = Commit.objects.get(node_id="commit-a")
    assert stored.created_at == commit.commit.author.date
    project = Project.objects.create(
        key="www-project-commit-sync-test",
        name="Commit sync test",
        summary="Local integration test",
        owasp_repository=repository,
    )
    project.repositories.add(repository)
    _, stats = Command().aggregate_contributions(project, START, END)
    assert stats["commits"] == 1
    state = RepositoryContributionSyncState.objects.get(
        repository=repository, contribution_type="commits"
    )
    assert state.covered_from == START
    assert state.covered_until == END
    assert state.last_head_sha == "f" * 40


def test_repeat_sync_preserves_commit_identity(source):
    remote, repository = source
    remote.get_commits.return_value = [github_commit("a")]
    run_sync(remote, repository)
    first = Commit.objects.get(node_id="commit-a")
    snapshot = MemberSnapshot.objects.create(
        github_user=User.objects.create(
            node_id="snapshot-user", login="snapshot-user", created_at=START, updated_at=END
        ),
        start_at=START,
        end_at=END,
    )
    snapshot.commits.add(first)
    run_sync(remote, repository)
    assert Commit.objects.filter(repository=repository).count() == 1
    assert Commit.objects.get(node_id="commit-a").pk == first.pk
    assert snapshot.commits.get().pk == first.pk


def test_history_is_pinned_and_filtered_by_author_date(source):
    remote, repository = source
    remote.get_commits.return_value = [
        github_commit("a", date=START - timedelta(seconds=1)),
        github_commit("b", date=START),
        github_commit("c", date=END),
        github_commit("d", date=END + timedelta(seconds=1)),
    ]
    run_sync(remote, repository)
    assert set(repository.commits.values_list("node_id", flat=True)) == {
        "commit-b",
        "commit-c",
        "commit-d",
    }
    remote.get_commits.assert_any_call(sha="f" * 40)
    project = Project.objects.create(
        key="www-project-future-commit",
        name="Future commit test",
        summary="Local test",
        owasp_repository=repository,
    )
    _, stats = Command().aggregate_contributions(project, START, END)
    assert stats["commits"] == 2
    # When the reporting period reaches the already stored future commit, it is counted.
    _, later_stats = Command().aggregate_contributions(project, START, END + timedelta(seconds=1))
    assert later_stats["commits"] == 3


def test_known_users_are_reused_and_preserved_when_unresolved(source, mocker):
    remote, repository = source
    author = User.objects.create(
        node_id="known-author", login="known-author", created_at=START, updated_at=END
    )
    account = SimpleNamespace(raw_data={"node_id": author.node_id})
    lookup = mocker.patch("apps.github.common.User.update_data")
    remote.get_commits.return_value = [github_commit("a", author=account, committer=account)]
    run_sync(remote, repository)
    lookup.assert_not_called()
    first = repository.commits.get()
    assert first.author_id == first.committer_id == author.pk
    remote.get_commits.return_value = [github_commit("a")]
    common.sync_repository_commits(remote, repository, force=True)
    first.refresh_from_db()
    assert first.author_id == first.committer_id == author.pk


@pytest.mark.parametrize("account_type", ["User", "Bot"])
def test_new_author_is_imported_once_and_shared_with_committer(source, mocker, account_type):
    remote, repository = source
    account = SimpleNamespace(
        raw_data={"node_id": "new-author"},
        login="new-author",
        type=account_type,
        avatar_url="https://example.com/avatar.png",
        name="New author",
        email="",
        collaborators=0,
        company="",
        created_at=START,
        updated_at=END,
        followers=0,
        following=0,
        location="",
        public_gists=0,
        public_repos=1,
    )
    imported = mocker.spy(User, "update_data")
    remote.get_commits.return_value = [
        github_commit("a", author=account, committer=account),
        github_commit("b", author=account, committer=account),
    ]
    run_sync(remote, repository)
    imported.assert_called_once_with(account)
    user = User.objects.get(node_id="new-author")
    assert user.is_bot == (account_type == "Bot")
    assert repository.commits.filter(author=user, committer=user).count() == 2


def test_unresolved_authors_do_not_drop_commits(source):
    remote, repository = source
    remote.get_commits.return_value = [github_commit("a")]
    run_sync(remote, repository)
    stored = repository.commits.get()
    assert stored.author_id is None
    assert stored.committer_id is None


@pytest.mark.parametrize("status", [404, 403])
def test_account_lookup_distinguishes_missing_from_forbidden(source, mocker, status):
    remote, repository = source
    account = SimpleNamespace(raw_data={"node_id": "disappeared-account"})
    lookup = mocker.patch(
        "apps.github.common.User.update_data",
        side_effect=UnknownObjectException(status, {"message": "Account lookup failed"}),
    )
    remote.get_commits.return_value = [
        github_commit("a", author=account, committer=account),
        github_commit("b", author=account),
    ]
    if status == 403:
        with pytest.raises(UnknownObjectException):
            run_sync(remote, repository)
        assert not repository.commits.exists()
        assert (
            repository.contribution_sync_states.get(contribution_type="commits").covered_until
            is None
        )
        return
    run_sync(remote, repository)
    lookup.assert_called_once_with(account)
    assert repository.commits.filter(author__isnull=True, committer__isnull=True).count() == 2


def test_partial_history_failure_keeps_checkpoint_and_retries_safely(source, mocker):
    remote, repository = source
    mocker.patch("apps.github.common.GITHUB_ITEMS_PER_PAGE", 2)
    state = RepositoryContributionSyncState.objects.create(
        repository=repository,
        contribution_type="commits",
        covered_from=START,
        covered_until=END - timedelta(days=1),
        default_branch="main",
        last_head_sha="e" * 40,
    )

    def interrupted():
        yield github_commit("a")
        yield github_commit("b")
        message = "sensitive-response-body"
        raise RuntimeError(message)

    remote.get_commits.side_effect = lambda **kwargs: interrupted() if kwargs else []
    with pytest.raises(RuntimeError, match="sensitive-response-body"):
        run_sync(remote, repository)
    state.refresh_from_db()
    assert repository.commits.count() == 2
    assert state.covered_until == END - timedelta(days=1)
    assert state.last_head_sha == "e" * 40
    assert state.last_error == "Commit import failed: RuntimeError"
    # A separate connection can acquire the lock after failure: no leaked session lock.
    with (
        closing(connection.Database.connect(**connection.get_connection_params())) as other,
        other.cursor() as cursor,
    ):
        cursor.execute(
            "SELECT pg_try_advisory_lock(hashtextextended(%s, 0))",
            [f"nest:github:commits-sync:{repository.pk}"],
        )
        assert cursor.fetchone()[0]

    ids = set(repository.commits.values_list("pk", flat=True))
    remote.get_commits.side_effect = None
    remote.get_commits.return_value = [github_commit("a"), github_commit("b"), github_commit("c")]
    run_sync(remote, repository)
    state.refresh_from_db()
    assert repository.commits.count() == 3
    assert ids <= set(repository.commits.values_list("pk", flat=True))
    assert state.covered_until == END
    assert state.last_head_sha == "f" * 40
    assert state.last_error == ""


def test_initial_failure_does_not_claim_complete_empty_history(source):
    remote, repository = source
    remote.get_branch.side_effect = GithubException(403, {"message": "private details"})
    with pytest.raises(GithubException):
        run_sync(remote, repository)
    state = repository.contribution_sync_states.get(contribution_type="commits")
    assert state.covered_from is None
    assert state.covered_until is None
    assert state.last_head_sha == ""
    assert "private details" not in state.last_error


@pytest.mark.parametrize("empty", [True, False])
def test_branch_lookup_failure_is_not_automatically_empty_history(source, mocker, empty):
    remote, repository = source
    remote.get_branch.side_effect = GithubException(404, {"message": "Not found"})
    count = Mock()
    if empty:
        mocker.patch.object(
            type(count),
            "totalCount",
            create=True,
            new_callable=PropertyMock,
            side_effect=GithubException(409, {"message": "Git Repository is empty."}),
        )
    else:
        count.totalCount = 1
    remote.get_commits.return_value = count
    if empty:
        run_sync(remote, repository)
    else:
        with pytest.raises(GithubException):
            run_sync(remote, repository)
    state = repository.contribution_sync_states.get(contribution_type="commits")
    assert state.covered_until == (END if empty else None)
    assert repository.commits.count() == 0


def test_archived_repositories_still_import_commit_history(source):
    remote, repository = source
    repository.is_archived = True
    repository.save(update_fields=("is_archived",))
    remote.get_commits.return_value = [github_commit("a")]
    run_sync(remote, repository)
    assert repository.commits.count() == 1


def test_duplicate_items_across_batches_are_upserted(source, mocker):
    remote, repository = source
    mocker.patch("apps.github.common.GITHUB_ITEMS_PER_PAGE", 2)
    remote.get_commits.return_value = [
        github_commit("a"),
        github_commit("a"),
        github_commit("b"),
        github_commit("a"),
    ]
    run_sync(remote, repository)
    assert repository.commits.count() == 2


def test_concurrent_repository_import_is_rejected_without_touching_checkpoint(source):
    remote, repository = source
    with (
        closing(connection.Database.connect(**connection.get_connection_params())) as other,
        other.cursor() as cursor,
    ):
        cursor.execute(
            "SELECT pg_advisory_lock(hashtextextended(%s, 0))",
            [f"nest:github:commits-sync:{repository.pk}"],
        )
        with pytest.raises(RuntimeError, match="already running"):
            run_sync(remote, repository)
    remote.get_branch.assert_not_called()
    assert not repository.contribution_sync_states.exists()
    run_sync(remote, repository)
    assert (
        repository.contribution_sync_states.get(contribution_type="commits").covered_until == END
    )


@pytest.mark.parametrize(("start", "end"), [(END.replace(tzinfo=None), END), (END, START)])
def test_invalid_period_is_rejected_before_writing_state(source, start, end):
    remote, repository = source
    with pytest.raises(ValueError, match="timezone-aware"):
        common.sync_repository_commits(remote, repository, start_at=start, end_at=end)
    assert not repository.contribution_sync_states.exists()


def test_failed_batch_rolls_back_and_does_not_advance_coverage(source):
    remote, repository = source
    invalid = github_commit("b")
    invalid.commit.message = None
    remote.get_commits.return_value = [github_commit("a"), invalid]
    with pytest.raises(IntegrityError):
        run_sync(remote, repository)
    assert not repository.commits.exists()
    state = repository.contribution_sync_states.get(contribution_type="commits")
    assert state.covered_until is None
    assert state.last_head_sha == ""
    assert state.last_error == "Commit import failed: IntegrityError"
    remote.get_commits.return_value = [github_commit("a"), github_commit("b")]
    run_sync(remote, repository)
    state.refresh_from_db()
    assert repository.commits.count() == 2
    assert state.covered_until == END
    assert state.last_error == ""


def test_failed_checkpoint_write_does_not_publish_a_new_head(source, mocker):
    remote, repository = source
    remote.get_commits.return_value = [github_commit("a")]
    save = RepositoryContributionSyncState.save

    def interrupted_save(state, *args, **kwargs):
        if "covered_until" in kwargs.get("update_fields", ()):
            message = "simulated checkpoint write failure"
            raise DatabaseError(message)
        return save(state, *args, **kwargs)

    mocker.patch.object(RepositoryContributionSyncState, "save", new=interrupted_save)
    with pytest.raises(DatabaseError, match="checkpoint write failure"):
        run_sync(remote, repository)
    assert repository.commits.count() == 1
    state = repository.contribution_sync_states.get(contribution_type="commits")
    assert state.covered_until is None
    assert state.covered_from is None
    assert state.last_head_sha == ""
    assert state.last_error == "Commit import failed: DatabaseError"


def test_same_sha_in_different_repositories_has_independent_identity(source):
    remote, repository = source
    commit = github_commit("a")
    remote.get_commits.return_value = [commit]
    run_sync(remote, repository)
    fork = Repository.objects.create(
        node_id="fork-repository",
        key="fork",
        name="fork",
        default_branch="main",
        created_at=START,
        updated_at=END,
        pushed_at=END,
    )
    commit.raw_data = {"node_id": "fork-commit-a"}
    commit.node_id = "fork-commit-a"
    common.sync_repository_commits(remote, fork)
    assert Commit.objects.filter(sha=commit.sha).count() == 2
    assert repository.commits.get().node_id == "commit-a"
    assert fork.commits.get().node_id == "fork-commit-a"


def test_conflicting_repository_identity_does_not_move_existing_commit(source):
    remote, repository = source
    remote.get_commits.return_value = [github_commit("a")]
    run_sync(remote, repository)
    other = Repository.objects.create(
        node_id="other-repository",
        key="other",
        name="other",
        created_at=START,
        updated_at=END,
        pushed_at=END,
    )
    with pytest.raises(ValueError, match="different repository"):
        common.sync_repository_commits(remote, other)
    assert repository.commits.get().node_id == "commit-a"
    assert not other.commits.exists()
    assert other.contribution_sync_states.get().covered_until is None


def checkpoint(repository, **overrides):
    values = {
        "covered_from": START,
        "covered_until": END - timedelta(days=1),
        "default_branch": "main",
        "last_head_sha": "e" * 40,
    }
    values.update(overrides)
    return RepositoryContributionSyncState.objects.create(
        repository=repository, contribution_type="commits", **values
    )


def test_unchanged_head_skips_history_and_extends_coverage(source):
    remote, repository = source
    state = checkpoint(repository, last_head_sha="f" * 40)
    common.sync_repository_commits(remote, repository)
    remote.compare.assert_not_called()
    remote.get_commits.assert_not_called()
    state.refresh_from_db()
    assert state.covered_until == END


def test_incremental_comparison_imports_more_than_250_commits(source):
    remote, repository = source
    state = checkpoint(repository)
    comparison = remote.compare.return_value
    comparison.status = "ahead"
    commits = [github_commit(str(index)) for index in range(305)]
    # SHA is independent of the synthetic identity, and fits the database field.
    for index, commit in enumerate(commits):
        commit.sha = f"{index:040x}"
    comparison.total_commits = len(commits)
    comparison.get_commits.return_value = iter(commits)
    common.sync_repository_commits(remote, repository)
    remote.compare.assert_called_once_with("e" * 40, "f" * 40)
    comparison.get_commits.assert_called_once_with(comparison_commits_per_page=100)
    remote.get_commits.assert_not_called()
    assert repository.commits.count() == 305
    state.refresh_from_db()
    assert state.last_head_sha == "f" * 40
    common.sync_repository_commits(remote, repository)
    assert repository.commits.count() == 305
    assert remote.compare.call_count == 1


@pytest.mark.parametrize("reason", ["branch", "older_period", "force", "missing_head"])
def test_incompatible_checkpoint_uses_full_history(source, reason):
    remote, repository = source
    state = checkpoint(repository)
    kwargs = {}
    if reason == "branch":
        remote.default_branch = "renamed"
    elif reason == "older_period":
        kwargs["start_at"] = START - timedelta(days=1)
    elif reason == "force":
        kwargs["force"] = True
    else:
        state.last_head_sha = ""
        state.save()
    remote.get_commits.return_value = [github_commit("a")]
    common.sync_repository_commits(remote, repository, **kwargs)
    remote.compare.assert_not_called()
    remote.get_commits.assert_called_once_with(sha="f" * 40)
    assert repository.commits.count() == 1
    state.refresh_from_db()
    assert state.covered_from == kwargs.get("start_at", START)


@pytest.mark.parametrize("status", ["diverged", "behind", "identical", "oversized", 404, 409])
def test_unusable_comparison_falls_back_without_deleting_history(source, status):
    remote, repository = source
    checkpoint(repository)
    original = Commit.objects.create(
        node_id="previous-history",
        repository=repository,
        sha="a" * 40,
        message="Previously imported",
        created_at=START,
    )
    if isinstance(status, int):
        remote.compare.side_effect = GithubException(status, {"message": "Unavailable"})
    else:
        remote.compare.return_value.status = "ahead" if status == "oversized" else status
        remote.compare.return_value.total_commits = 10_001
    remote.get_commits.return_value = [github_commit("b")]
    common.sync_repository_commits(remote, repository)
    remote.get_commits.assert_called_once_with(sha="f" * 40)
    assert repository.commits.filter(pk=original.pk).exists()
    assert repository.commits.count() == 2


@pytest.mark.parametrize("status", [403, 429, 500])
def test_comparison_service_errors_preserve_checkpoint(source, status):
    remote, repository = source
    state = checkpoint(repository)
    remote.compare.side_effect = GithubException(status, {"message": "private response"})
    with pytest.raises(GithubException):
        common.sync_repository_commits(remote, repository)
    state.refresh_from_db()
    assert state.last_head_sha == "e" * 40
    assert state.covered_until == END - timedelta(days=1)
    assert "private response" not in state.last_error
    remote.get_commits.assert_not_called()


def test_truncated_comparison_cannot_advance_checkpoint_and_can_retry(source, mocker):
    remote, repository = source
    state = checkpoint(repository)
    mocker.patch("apps.github.common.GITHUB_ITEMS_PER_PAGE", 1)
    comparison = remote.compare.return_value
    comparison.status = "ahead"
    comparison.total_commits = 2
    comparison.get_commits.return_value = [github_commit("a")]
    with pytest.raises(RuntimeError, match="incomplete history"):
        common.sync_repository_commits(remote, repository)
    first = repository.commits.get()
    state.refresh_from_db()
    assert state.last_head_sha == "e" * 40
    assert state.covered_until == END - timedelta(days=1)
    comparison.get_commits.return_value = [github_commit("a"), github_commit("b")]
    common.sync_repository_commits(remote, repository)
    assert repository.commits.get(node_id="commit-a").pk == first.pk
    assert repository.commits.count() == 2
    state.refresh_from_db()
    assert state.last_head_sha == "f" * 40
    assert state.last_error == ""


def test_real_github_comparison_follows_pagination(source):
    """Exercise the installed client's pagination instead of a plain list stand-in."""
    remote, repository = source
    checkpoint(repository)
    requester = Mock()
    requester.per_page = 100
    requester.is_lazy = False
    url = "https://api.github.com/repos/example/repo/compare/old...new"

    def page(start, stop):
        return {
            "commits": [
                {
                    "node_id": f"paged-{index}",
                    "sha": f"{index:040x}",
                    "commit": {
                        "message": "Paged commit",
                        "author": {"date": "2026-06-01T12:00:00Z"},
                    },
                    "author": None,
                    "committer": None,
                }
                for index in range(start, stop)
            ]
        }

    requester.requestJsonAndCheck.side_effect = [
        ({"link": f'<{url}?page=2&per_page=100>; rel="next"'}, page(0, 100)),
        ({"link": f'<{url}?page=3&per_page=100>; rel="next"'}, page(100, 200)),
        ({"link": f'<{url}?page=4&per_page=100>; rel="next"'}, page(200, 300)),
        ({}, page(300, 305)),
    ]
    remote.compare.return_value = Comparison(
        requester, {}, {"url": url, "status": "ahead", "total_commits": 305}, completed=True
    )
    common.sync_repository_commits(remote, repository)
    assert repository.commits.count() == 305
    assert requester.requestJsonAndCheck.call_count == 4
    assert (
        repository.contribution_sync_states.get(contribution_type="commits").last_head_sha
        == "f" * 40
    )


@pytest.fixture(params=["issues", "pull_requests"])
def activity(request):
    if request.param == "issues":
        return SimpleNamespace(
            kind="issues", model=Issue, fetch="get_issues", sync=common.sync_repository_issues
        )
    return SimpleNamespace(
        kind="pull_requests",
        model=PullRequest,
        fetch="get_pulls",
        sync=common.sync_repository_pull_requests,
    )


def github_activity(key, *, created_at=None, updated_at=None):
    return SimpleNamespace(
        raw_data={"node_id": f"activity-{key}"},
        body="Activity test",
        comments=0,
        closed_at=END,
        created_at=created_at or END - timedelta(days=180),
        updated_at=updated_at or END - timedelta(days=180),
        locked=False,
        active_lock_reason=None,
        number=1,
        id=1,
        state="closed",
        state_reason="completed",
        title=f"Activity {key}",
        html_url="https://github.com/example/repo/issues/1",
        merged_at=None,
        pull_request=None,
        milestone=None,
        user=None,
        assignees=[],
        labels=[],
    )


def activity_state(repository, kind):
    return repository.contribution_sync_states.get(contribution_type=kind)


def test_activity_backfill_is_independent_of_recent_rows(source, activity):
    remote, repository = source
    recent = github_activity("recent", created_at=END, updated_at=END)
    activity.model.update_data(recent, repository=repository)
    old = github_activity("old")
    boundary = github_activity("boundary", created_at=START, updated_at=START)
    outside = github_activity("outside", updated_at=START - timedelta(seconds=1))
    getattr(remote, activity.fetch).return_value = [recent, old, boundary, outside]
    activity.sync(remote, repository)
    assert set(activity.model.objects.values_list("node_id", flat=True)) == {
        "activity-recent",
        "activity-old",
        "activity-boundary",
    }
    state = activity_state(repository, activity.kind)
    assert (state.covered_from, state.covered_until) == (START, END)
    ids = set(activity.model.objects.values_list("pk", flat=True))
    activity.sync(remote, repository)
    assert set(activity.model.objects.values_list("pk", flat=True)) == ids


def test_activity_uses_overlap_and_refreshes_old_contributions(source, activity):
    remote, repository = source
    state = RepositoryContributionSyncState.objects.create(
        repository=repository,
        contribution_type=activity.kind,
        covered_from=START,
        covered_until=END - timedelta(days=1),
    )
    cutoff = END - timedelta(days=2)
    at_boundary = github_activity("boundary", created_at=START, updated_at=cutoff)
    before_boundary = github_activity("before", updated_at=cutoff - timedelta(seconds=1))
    getattr(remote, activity.fetch).return_value = [at_boundary, before_boundary]
    activity.sync(remote, repository)
    assert activity.model.objects.get().node_id == "activity-boundary"
    at_boundary.title = "Refreshed title"
    at_boundary.updated_at = END
    activity.sync(remote, repository)
    assert activity.model.objects.get().title == "Refreshed title"
    state.refresh_from_db()
    assert state.covered_until == END
    getattr(remote, activity.fetch).assert_called_with(
        direction="desc", sort="updated", state="all"
    )


@pytest.mark.parametrize("reason", ["force", "older_period", "gap"])
def test_activity_backfills_when_checkpoint_cannot_cover_request(source, activity, reason):
    remote, repository = source
    previous_end = END - timedelta(days=400) if reason == "gap" else END - timedelta(days=1)
    RepositoryContributionSyncState.objects.create(
        repository=repository,
        contribution_type=activity.kind,
        covered_from=previous_end - timedelta(days=365),
        covered_until=previous_end,
    )
    kwargs = {}
    if reason == "force":
        kwargs["force"] = True
    elif reason == "older_period":
        kwargs["start_at"] = START - timedelta(days=500)
    # The old requested period must be earlier than the existing coverage.
    old = github_activity("backfill", updated_at=START)
    getattr(remote, activity.fetch).return_value = [old]
    activity.sync(remote, repository, **kwargs)
    assert activity.model.objects.get().node_id == "activity-backfill"
    assert activity_state(repository, activity.kind).covered_from == kwargs.get("start_at", START)


def test_activity_interrupted_initial_backfill_retries_from_original_start(source, activity):
    remote, repository = source

    def interrupted():
        yield github_activity("recent", updated_at=END)
        message = "sensitive-source-response"
        raise RuntimeError(message)

    getattr(remote, activity.fetch).return_value = interrupted()
    with pytest.raises(RuntimeError, match="sensitive-source-response"):
        activity.sync(remote, repository)
    first = activity.model.objects.get()
    state = activity_state(repository, activity.kind)
    assert state.covered_from is None
    assert state.covered_until is None
    assert state.last_error == "Activity import failed: RuntimeError"
    getattr(remote, activity.fetch).return_value = [
        github_activity("recent", updated_at=END),
        github_activity("old"),
    ]
    activity.sync(remote, repository)
    assert activity.model.objects.count() == 2
    assert activity.model.objects.get(node_id="activity-recent").pk == first.pk
    state.refresh_from_db()
    assert state.covered_until == END
    assert state.last_error == ""


def test_activity_failed_incremental_sync_preserves_successful_checkpoint(source, activity):
    remote, repository = source
    state = RepositoryContributionSyncState.objects.create(
        repository=repository,
        contribution_type=activity.kind,
        covered_from=START,
        covered_until=END - timedelta(days=1),
    )
    getattr(remote, activity.fetch).side_effect = GithubException(403, {"message": "private"})
    with pytest.raises(GithubException):
        activity.sync(remote, repository)
    state.refresh_from_db()
    assert (state.covered_from, state.covered_until) == (START, END - timedelta(days=1))
    assert "private" not in state.last_error


def test_activity_empty_history_records_successful_coverage(source, activity):
    remote, repository = source
    activity.sync(remote, repository)
    assert activity_state(repository, activity.kind).covered_until == END
    assert activity.model.objects.count() == 0


def test_normal_sync_imports_archived_issue_and_pull_request_history(source):
    remote, repository = source
    repository.is_archived = True
    repository.save()
    remote.get_issues.return_value = [github_activity("issue")]
    remote.get_pulls.return_value = [github_activity("pr")]
    run_sync(remote, repository)
    assert repository.issues.count() == repository.pull_requests.count() == 1
    assert repository.contribution_sync_states.filter(covered_until=END).count() == 3
    remote.get_milestones.assert_not_called()


def test_disabled_issue_tracking_does_not_claim_coverage_or_block_pull_requests(source):
    remote, repository = source
    repository.track_issues = False
    repository.save()
    remote.get_pulls.return_value = [github_activity("pr")]
    run_sync(remote, repository)
    assert not repository.contribution_sync_states.filter(contribution_type="issues").exists()
    assert repository.pull_requests.count() == 1
    remote.get_issues.assert_not_called()


def test_issue_endpoint_pull_requests_do_not_become_issue_records(source):
    remote, repository = source
    pr = github_activity("pr")
    pr.pull_request = True
    remote.get_issues.return_value = [pr, github_activity("issue")]
    common.sync_repository_issues(remote, repository)
    assert repository.issues.get().node_id == "activity-issue"


def test_activity_checkpoint_write_failure_remains_retryable(source, activity, mocker):
    remote, repository = source
    getattr(remote, activity.fetch).return_value = [github_activity("saved")]
    original_save = RepositoryContributionSyncState.save

    def fail_checkpoint(state, *args, **kwargs):
        if "covered_until" in kwargs.get("update_fields", ()):
            message = "checkpoint unavailable"
            raise DatabaseError(message)
        return original_save(state, *args, **kwargs)

    mocker.patch.object(RepositoryContributionSyncState, "save", new=fail_checkpoint)
    with pytest.raises(DatabaseError, match="checkpoint unavailable"):
        activity.sync(remote, repository)
    assert activity.model.objects.count() == 1
    state = activity_state(repository, activity.kind)
    assert state.covered_until is None
    assert state.last_error == "Activity import failed: DatabaseError"


@pytest.mark.parametrize(("start", "end"), [(END.replace(tzinfo=None), END), (END, START)])
def test_activity_rejects_invalid_period_without_checkpoint(source, activity, start, end):
    remote, repository = source
    with pytest.raises(ValueError, match="timezone-aware"):
        activity.sync(remote, repository, start_at=start, end_at=end)
    assert not repository.contribution_sync_states.exists()


def test_activity_lock_rejects_concurrent_collection(source, activity):
    remote, repository = source
    with (
        closing(connection.Database.connect(**connection.get_connection_params())) as other,
        other.cursor() as cursor,
    ):
        cursor.execute(
            "SELECT pg_advisory_lock(hashtextextended(%s, 0))",
            [f"nest:github:{activity.kind}-sync:{repository.pk}"],
        )
        with pytest.raises(RuntimeError, match="already running"):
            activity.sync(remote, repository)
    assert not repository.contribution_sync_states.exists()
    getattr(remote, activity.fetch).assert_not_called()
    activity.sync(remote, repository)
    assert activity_state(repository, activity.kind).covered_until == END


def test_project_issue_tracking_setting_is_preserved(source):
    remote, repository = source
    project = Project.objects.create(
        key="www-project-disabled-issues",
        name="Disabled issues",
        summary="Test",
        owasp_repository=repository,
        track_issues=False,
    )
    project.repositories.add(repository)
    common.sync_repository_issues(remote, repository)
    remote.get_issues.assert_not_called()
    assert not repository.contribution_sync_states.exists()


def test_normal_sync_activity_reaches_project_aggregation(source, mocker):
    remote, repository = source
    # Preserve the existing model save behavior without invoking AI in a synthetic test.
    mocker.patch.object(Issue, "generate_hint")
    mocker.patch.object(Issue, "generate_summary")
    issue = github_activity("open")
    issue.state = "open"
    issue.closed_at = None
    remote.get_issues.return_value = [issue, github_activity("closed")]
    remote.get_pulls.return_value = [github_activity("pr")]
    project = Project.objects.create(
        key="www-project-activity",
        name="Activity",
        summary="Test",
        owasp_repository=repository,
    )
    run_sync(remote, repository)
    _, stats = Command().aggregate_contributions(project, START, END)
    assert stats["issues"] == 2
    assert stats["pull_requests"] == 1
    assert repository.issues.filter(state="open").count() == 1


def test_contribution_repository_selection_matches_active_entity_views(
    source, django_assert_num_queries
):
    _, repository = source

    def make_repository(key):
        return Repository.objects.create(
            node_id=f"selection-{key}",
            name=key,
            key=key,
            created_at=START,
            updated_at=END,
            pushed_at=END,
        )

    project_site = make_repository("www-project-active")
    chapter_site = make_repository("www-chapter-active")
    inactive_site = make_repository("www-project-inactive")
    inactive_chapter_site = make_repository("www-chapter-inactive")
    unrelated = make_repository("unrelated")
    project = Project.objects.create(
        key="www-project-selection",
        name="Selection",
        summary="Test",
        owasp_repository=project_site,
    )
    project.repositories.add(repository, project_site)
    # Multiple associations must not cause duplicate synchronization.
    other = Project.objects.create(key="www-project-selection-other", name="Other", summary="Test")
    other.repositories.add(repository)
    Chapter.objects.create(
        latitude=1,
        longitude=1,
        suggested_location="Test location",
        key="www-chapter-selection",
        name="Selection",
        owasp_repository=chapter_site,
    )
    inactive = Project.objects.create(
        key="www-project-inactive-selection",
        name="Inactive",
        summary="Test",
        is_active=False,
        owasp_repository=inactive_site,
    )
    inactive.repositories.add(unrelated)
    Chapter.objects.create(
        latitude=1,
        longitude=1,
        suggested_location="Test location",
        key="www-chapter-inactive-selection",
        name="Inactive",
        is_active=False,
        owasp_repository=inactive_chapter_site,
    )
    with django_assert_num_queries(1):
        selected = list(common.get_contribution_repositories().values_list("pk", flat=True))
    assert set(selected) == {repository.pk, project_site.pk, chapter_site.pk}
    assert len(selected) == len(set(selected))


@pytest.mark.parametrize(
    ("link", "included"),
    [
        ("project_primary", True),
        ("project_related", True),
        ("chapter", True),
        ("inactive", False),
        ("unlinked", False),
        ("other_identity", False),
    ],
)
def test_organization_command_syncs_only_linked_active_website_repositories(
    source, mocker, link, included
):
    remote, repository = source
    repository.name = repository.key = (
        "www-chapter-selection" if link == "chapter" else "www-project-selection"
    )
    repository.save()
    remote.name = repository.name
    remote.node_id = repository.node_id
    if link in ("project_primary", "inactive", "other_identity"):
        Project.objects.create(
            key="www-project-command-selection",
            name="Selection",
            summary="Test",
            owasp_repository=repository,
            is_active=link != "inactive",
        )
    elif link == "project_related":
        project = Project.objects.create(
            key="www-project-command-selection",
            name="Selection",
            summary="Test",
        )
        project.repositories.add(repository)
    elif link == "chapter":
        Chapter.objects.create(
            latitude=1,
            longitude=1,
            suggested_location="Test location",
            key="www-chapter-command-selection",
            name="Selection",
            owasp_repository=repository,
        )
    if link == "other_identity":
        remote.node_id = "different-repository-with-same-name"
    remote.get_commits.return_value = [github_commit("a")]
    command_module = "apps.github.management.commands.github_update_owasp_organization"
    client = mocker.patch(f"{command_module}.get_github_client").return_value
    client.get_organization.return_value.get_repo.return_value = remote
    # Exercise the real command, selection, collector, persistence and aggregation.
    # Only owner metadata fetching is bypassed, as in the other source fixtures.
    synced = mocker.patch(
        f"{command_module}.sync_repository",
        side_effect=lambda gh_repository, **kwargs: common.sync_repository(
            gh_repository, user=Mock(), organization=kwargs.get("organization")
        ),
    )
    SyncCommand().handle(repository=repository.name, offset=0)
    assert synced.call_count == int(included)
    assert repository.commits.count() == int(included)
    assert repository.contribution_sync_states.count() == (3 if included else 0)
    if included:
        entity = Chapter.objects.get() if link == "chapter" else Project.objects.get()
        _, stats = Command().aggregate_contributions(entity, START, END)
        assert stats["commits"] == 1
    client.close.assert_called_once()


def test_repair_refresh_updates_only_affected_entities_and_exact_period(source):
    remote, repository = source
    remote.get_commits.return_value = [github_commit("a")]
    common.sync_repository_commits(remote, repository)
    project = Project.objects.create(
        key="www-project-refresh",
        name="Refresh",
        summary="Test",
        owasp_repository=repository,
    )
    project.repositories.add(repository)
    unrelated = Project.objects.create(
        key="www-project-unrelated-refresh",
        name="Unrelated",
        summary="Test",
        contribution_stats={"total": 123},
    )
    RepairCommand().refresh_activity([repository], START, END)
    project.refresh_from_db()
    unrelated.refresh_from_db()
    assert project.contribution_stats["commits"] == 1
    assert project.contribution_stats["start_at"] == START.isoformat()
    assert project.contribution_stats["end_at"] == END.isoformat()
    assert unrelated.contribution_stats == {"total": 123}


@pytest.mark.parametrize("kind", ["commits", "issues", "pull_requests"])
def test_member_aggregation_includes_dated_activity_with_zero_counter(source, kind):
    _, repository = source
    user = User.objects.create(
        node_id="zero-counter",
        login="zero-counter",
        created_at=START,
        updated_at=END,
        contributions_count=0,
    )
    unrelated = User.objects.create(
        node_id="no-activity",
        login="no-activity",
        created_at=START,
        updated_at=END,
        contributions_count=0,
        contribution_data={"sentinel": 1},
    )
    if kind == "commits":
        Commit.objects.create(
            node_id="member-commit",
            repository=repository,
            author=user,
            sha="a" * 40,
            message="Test",
            created_at=END,
        )
    else:
        model = Issue if kind == "issues" else PullRequest
        model.update_data(
            github_activity("member", created_at=END), repository=repository, author=user
        )
    MemberCommand().handle(user=None, days=365, batch_size=100)
    user.refresh_from_db()
    unrelated.refresh_from_db()
    assert sum(user.contribution_data.values()) == 1
    assert unrelated.contribution_data == {"sentinel": 1}
    assert user.contributions_count == 0


def test_snapshot_repair_preserves_dates_and_slack_fields(source):
    _, repository = source
    user = User.objects.create(
        node_id="repair-user", login="repair-user", created_at=START, updated_at=END
    )
    repository.owner = user
    repository.save()
    snapshot = MemberSnapshot.objects.create(
        github_user=user,
        start_at=START,
        end_at=END,
        communication_heatmap_data={"slack": 3},
        channel_communications={"channel": 3},
    )
    commit = Commit.objects.create(
        node_id="repair-commit",
        repository=repository,
        author=user,
        sha="a" * 40,
        message="Test",
        created_at=END,
    )
    call_command("owasp_repair_member_snapshots", snapshot.pk)
    call_command("owasp_repair_member_snapshots", snapshot.pk)
    snapshot.refresh_from_db()
    assert snapshot.commits.get().pk == commit.pk
    assert (snapshot.start_at, snapshot.end_at) == (START, END)
    assert snapshot.communication_heatmap_data == {"slack": 3}
    assert snapshot.channel_communications == {"channel": 3}


def test_member_save_rechecks_identity_after_repository_import(source):
    remote, repository = source
    author = User.objects.create(
        node_id="race-author", login="race-author", created_at=START, updated_at=END
    )
    stale = Commit(
        node_id="commit-a",
        repository=repository,
        sha="a" * 40,
        message="Member search",
        created_at=END,
    )
    remote.get_commits.return_value = [github_commit("a")]
    common.sync_repository_commits(remote, repository)
    existing = repository.commits.get()
    existing.author = author
    existing.save()
    snapshot = MemberSnapshot.objects.create(github_user=author, start_at=START, end_at=END)
    snapshot.commits.add(existing)
    Commit.bulk_save([stale])
    assert repository.commits.count() == 1
    assert snapshot.commits.get().pk == existing.pk
    existing.refresh_from_db()
    assert existing.author_id == author.pk


@pytest.mark.django_db(transaction=True)
def test_member_writer_waits_for_repository_lock(source):
    _, repository = source
    started = Event()

    def save_member():
        close_old_connections()
        try:
            stale = Commit(
                node_id="simultaneous",
                repository=repository,
                sha="b" * 40,
                message="Member",
                created_at=END,
            )
            started.set()
            Commit.bulk_save([stale])
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=1) as pool:
        with common._repository_contribution_sync_lock(repository, "commits"):
            future = pool.submit(save_member)
            assert started.wait(timeout=5)
            with pytest.raises(TimeoutError):
                future.result(timeout=0.2)
            existing = Commit.objects.create(
                node_id="simultaneous",
                repository=repository,
                sha="b" * 40,
                message="Repository",
                created_at=END,
            )
        future.result(timeout=10)
    assert repository.commits.get(node_id="simultaneous").pk == existing.pk


def test_snapshot_repair_preserves_real_message_relationship_and_rolls_back(source, mocker):
    _, _repository = source
    user = User.objects.create(
        node_id="slack-preservation", login="slack-preservation", created_at=START, updated_at=END
    )
    _repository.owner = user
    _repository.save()
    conversation = Conversation.objects.create(
        slack_channel_id="CLOCALTEST",
        name="local-test",
        workspace=Workspace.objects.create(name="Local test", slack_workspace_id="TLOCALTEST"),
    )
    message = Message.objects.create(
        conversation=conversation,
        slack_message_id="1.0",
        created_at=END,
        raw_data={"text": "test"},
    )
    snapshot = MemberSnapshot.objects.create(
        github_user=user, start_at=START, end_at=END, communication_heatmap_data={"saved": 3}
    )
    snapshot.messages.add(message)
    call_command("owasp_repair_member_snapshots", snapshot.pk)
    snapshot.refresh_from_db()
    assert snapshot.messages.get().pk == message.pk
    assert snapshot.communication_heatmap_data == {"saved": 3}
    old = snapshot.contribution_heatmap_data
    Commit.objects.create(
        node_id="rollback-commit",
        repository=_repository,
        author=user,
        sha="c" * 40,
        message="New activity",
        created_at=END,
    )
    generation = mocker.patch(
        "apps.owasp.management.commands.owasp_repair_member_snapshots.SnapshotCommand.generate_repository_contributions",
        side_effect=RuntimeError("interrupted"),
    )
    with pytest.raises(RuntimeError):
        call_command("owasp_repair_member_snapshots", snapshot.pk)
    snapshot.refresh_from_db()
    assert snapshot.messages.get().pk == message.pk
    assert snapshot.contribution_heatmap_data == old
    assert snapshot.commits.count() == 0
    mocker.stop(generation)
    with pytest.raises(CommandError):
        call_command("owasp_repair_member_snapshots", snapshot.pk, 999999999)
    snapshot.refresh_from_db()
    assert snapshot.contribution_heatmap_data == old


def test_repair_command_database_selection_batching_and_partial_failure(source, mocker):
    _remote, repository = source
    owner = User.objects.create(
        node_id="operator-owner", login="operator-owner", created_at=START, updated_at=END
    )
    repository.owner = owner
    repository.save()
    second = Repository.objects.create(
        node_id="operator-second",
        name="second",
        key="second",
        owner=owner,
        created_at=START,
        updated_at=END,
        pushed_at=END,
    )
    project = Project.objects.create(key="www-project-operator", name="Operator", summary="Test")
    project.repositories.add(repository, second)
    module = "apps.github.management.commands.github_sync_contributions"
    client = mocker.patch(f"{module}.get_github_client").return_value
    client.get_repo.side_effect = lambda path: SimpleNamespace(
        node_id=repository.node_id if path == repository.path else second.node_id
    )
    commits = mocker.patch(f"{module}.sync_repository_commits")
    issues = mocker.patch(f"{module}.sync_repository_issues")
    refresh = mocker.patch(f"{module}.Command.refresh_activity")
    call_command(
        "github_sync_contributions",
        "--organization",
        owner.login,
        "--offset",
        "1",
        "--limit",
        "1",
        "--types",
        "commits",
    )
    assert commits.call_args.args[1].pk == second.pk
    commits.reset_mock()
    commits.side_effect = [RuntimeError("private-body"), None]
    with pytest.raises(CommandError, match="incomplete"):
        call_command(
            "github_sync_contributions",
            "--organization",
            owner.login,
            "--types",
            "commits",
            "issues",
            "--refresh",
        )
    assert commits.call_count == 2
    assert issues.call_count == 2
    refresh.assert_not_called()
