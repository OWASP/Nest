"""Exercise repository commit ingestion with real persistence and aggregation."""

from contextlib import closing
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock, PropertyMock

import pytest
from django.db import DatabaseError, IntegrityError, connection
from github.Comparison import Comparison
from github.GithubException import GithubException, UnknownObjectException

from apps.core.utils.index import disable_indexing
from apps.github import common
from apps.github.common import sync_repository
from apps.github.models.commit import Commit
from apps.github.models.repository import Repository
from apps.github.models.repository_contribution_sync_state import RepositoryContributionSyncState
from apps.github.models.user import User
from apps.owasp.management.commands.owasp_aggregate_entity_contributions import Command
from apps.owasp.models.member_snapshot import MemberSnapshot
from apps.owasp.models.project import Project

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
        assert repository.contribution_sync_states.get().covered_until is None
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
            [f"nest:github:commit-sync:{repository.pk}"],
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
            [f"nest:github:commit-sync:{repository.pk}"],
        )
        with pytest.raises(RuntimeError, match="already running"):
            run_sync(remote, repository)
    remote.get_branch.assert_not_called()
    assert not repository.contribution_sync_states.exists()
    run_sync(remote, repository)
    assert repository.contribution_sync_states.get().covered_until == END


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
    state = repository.contribution_sync_states.get()
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
    state = repository.contribution_sync_states.get()
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
    assert repository.contribution_sync_states.get().last_head_sha == "f" * 40
