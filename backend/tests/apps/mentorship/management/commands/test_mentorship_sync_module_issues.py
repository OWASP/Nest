import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import datetime as dt
from django.utils import timezone

from apps.mentorship.management.commands.mentorship_sync_module_issues import Command
from apps.mentorship.models.task import Task
from github.GithubException import GithubException


def make_qs(iterable, exists=True):
    """Return a queryset-like MagicMock that is iterable and supports .exists()."""
    qs = MagicMock(name="QuerySet")
    qs.exists.return_value = exists
    qs.__iter__.return_value = iter(iterable)
    qs.all.return_value = list(iterable)
    return qs


@pytest.fixture
def command():
    cmd = Command()
    cmd.stdout = MagicMock()
    cmd.stderr = MagicMock()
    cmd.style = MagicMock()
    cmd.style.WARNING = lambda x: x
    cmd.style.SUCCESS = lambda x: x
    cmd.style.ERROR = lambda x: x
    return cmd


def test_extract_repo_full_name_from_object(command):
    repo = MagicMock()
    repo.path = "owner/repo-name"
    assert command._extract_repo_full_name(repo) == "owner/repo-name"


@pytest.mark.parametrize(
    "repo_url, expected",
    [
        ("https://github.com/owner/repo", "owner/repo"),
        ("https://www.github.com/owner/repo/sub/path", "owner/repo"),
        ("https://invalid.com/owner/repo", None),
        ("not-a-url", None),
        ("https://github.com/owner", None),
        (None, None),
    ],
)
def test_extract_repo_full_name_from_url(command, repo_url, expected):
    assert command._extract_repo_full_name(repo_url) == expected


def test_get_status_variants(command):
    issue = MagicMock(); issue.state = "closed"
    assert command._get_status(issue, MagicMock()) == Task.Status.COMPLETED

    issue.state = "open"
    assert command._get_status(issue, MagicMock()) == Task.Status.IN_PROGRESS
    assert command._get_status(issue, None) == Task.Status.TODO


def test_get_last_assigned_date_found_and_not_found_and_exception(command):
    mock_repo = MagicMock()
    mock_issue_gh = MagicMock()
    mock_repo.get_issue.return_value = mock_issue_gh

    e1 = MagicMock(event="commented", created_at=datetime(2023, 1, 1, tzinfo=dt.timezone.utc))
    e2 = MagicMock(event="assigned", assignee=MagicMock(login="other"), created_at=datetime(2023, 1, 2, tzinfo=dt.timezone.utc))
    e3 = MagicMock(event="assigned", assignee=MagicMock(login="target"), created_at=datetime(2023, 1, 3, tzinfo=dt.timezone.utc))
    e4 = MagicMock(event="assigned", assignee=MagicMock(login="target"), created_at=datetime(2023, 1, 5, tzinfo=dt.timezone.utc))
    mock_issue_gh.get_events.return_value = [e1, e2, e3, e4]

    res = command._get_last_assigned_date(mock_repo, 123, "target")
    assert res == datetime(2023, 1, 5, tzinfo=dt.timezone.utc)

    # not found
    mock_issue_gh.get_events.return_value = [e1, e2]
    res2 = command._get_last_assigned_date(mock_repo, 123, "target")
    assert res2 is None
    
    mock_repo.get_issue.side_effect = GithubException("some gh error")
    r3 = command._get_last_assigned_date(mock_repo, 1, "target")
    assert r3 is None
    assert command.stderr.write.called


def test_build_repo_label_to_issue_map_iterable():
    rows = [
        (1, 10, "Label-A"),
        (2, 10, "label-b"),
        (3, 20, "Label-A"),
        (4, 10, "label-a"),
    ]

    with patch("apps.mentorship.management.commands.mentorship_sync_module_issues.Issue") as MockIssue:
        MockIssue.objects.filter.return_value.values_list.return_value.iterator.return_value = iter(rows)

        cmd = Command()
        cmd.stdout = MagicMock()
        cmd.style = MagicMock()
        cmd.style.SUCCESS = lambda x: x
        repo_label_map = cmd._build_repo_label_to_issue_map()

        assert (10, "label-a") in repo_label_map
        assert repo_label_map[(10, "label-a")] == {1, 4}
        assert repo_label_map[(10, "label-b")] == {2}
        assert repo_label_map[(20, "label-a")] == {3}
        cmd.stdout.write.assert_any_call("Map built. Found issues for 3 unique repo-label pairs.")


@patch("apps.mentorship.management.commands.mentorship_sync_module_issues.Task")
@patch("apps.mentorship.management.commands.mentorship_sync_module_issues.Issue")
def test_process_module_links_and_creates_tasks(MockIssue, MockTask, command):
    mock_repo = MagicMock(); mock_repo.id = 77; mock_repo.name = "repo-name"
    mock_module = MagicMock()
    mock_module.id = 11
    mock_module.name = "Test Module"
    mock_module.labels = ["module-label-1"]
    mock_project_repo = MagicMock(); mock_project_repo.id = mock_repo.id; mock_project_repo.name = mock_repo.name
    mock_module.project.repositories.all.return_value = [mock_project_repo]
    MockTask.Status = Task.Status


    repo_label_to_issue_ids = {(mock_repo.id, "module-label-1"): {1, 2, 3}}

    assignee = MagicMock(); assignee.login = "assignee1"
    issue1 = MagicMock(id=1, number=1, state="open", repository=mock_project_repo)
    issue2 = MagicMock(id=2, number=2, state="closed", repository=mock_project_repo)
    issue3 = MagicMock(id=3, number=3, state="open", repository=mock_project_repo)

    issue1.assignees.first.return_value = assignee
    issue2.assignees.first.return_value = assignee
    issue3.assignees.first.return_value = None

    issues_qs = make_qs([issue1, issue2], exists=True)
    MockIssue.objects.filter.return_value.select_related.return_value.prefetch_related.return_value.distinct.return_value = issues_qs

    created_task1 = MagicMock(module=None, status=None, assigned_at=None)
    created_task2 = MagicMock(module=None, status=None, assigned_at=None)
    MockTask.objects.get_or_create.side_effect = [
        (created_task1, True),
        (created_task2, True),
    ]

    with patch("apps.mentorship.management.commands.mentorship_sync_module_issues.transaction.atomic") as mock_atomic:
        mock_atomic.return_value.__enter__.return_value = None
        mock_atomic.return_value.__exit__.return_value = None

        with patch.object(command, "_get_last_assigned_date", return_value=timezone.now()):
            num_linked = command._process_module(
                module=mock_module,
                repo_label_to_issue_ids=repo_label_to_issue_ids,
                gh_client=MagicMock(),
                repo_cache={},
                verbosity=1,
            )
    assert num_linked == 3

    mock_module.issues.set.assert_called_once_with({1, 2, 3})

    assert MockTask.objects.get_or_create.call_count == 2

    calls = MockTask.objects.get_or_create.call_args_list
    called_issues = {c.kwargs["issue"] for c in calls}
    called_statuses = {c.kwargs["defaults"]["status"] for c in calls}

    assert called_issues == {issue1, issue2}

    assert Task.Status.IN_PROGRESS in called_statuses
    assert Task.Status.COMPLETED in called_statuses

    found = False
    for c in calls:
        if c.kwargs["issue"] is issue1 and c.kwargs["defaults"]["status"] == Task.Status.IN_PROGRESS:
            found = True
            break
    assert found, "expected a get_or_create call for issue1 with IN_PROGRESS status"

    command.stdout.write.assert_any_call(command.style.SUCCESS(
        f"Updated module '{mock_module.name}': set 3 issues from repos: [{mock_project_repo.name}] and created 2 tasks."
    ))


def test_process_module_no_matches():
    mock_repo = MagicMock(); mock_repo.id = 7; mock_repo.name = "r"
    mock_module = MagicMock()
    mock_module.project.repositories.all.return_value = [mock_repo]
    mock_module.labels = ["some-label"]

    repo_label_to_issue_ids = {}

    with patch("apps.mentorship.management.commands.mentorship_sync_module_issues.Task") as MockTask, \
         patch("apps.mentorship.management.commands.mentorship_sync_module_issues.transaction.atomic") as mock_atomic:
        mock_atomic.return_value.__enter__.return_value = None
        mock_atomic.return_value.__exit__.return_value = None

        num_linked = Command()._process_module(
            module=mock_module,
            repo_label_to_issue_ids=repo_label_to_issue_ids,
            gh_client=MagicMock(),
            repo_cache={},
            verbosity=1,
        )

    mock_module.issues.set.assert_called_once_with(set())
    MockTask.objects.get_or_create.assert_not_called()
    assert num_linked == 0
