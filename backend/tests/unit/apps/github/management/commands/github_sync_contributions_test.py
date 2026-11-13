"""Check repair command boundaries and failure reporting."""

from io import StringIO
from unittest.mock import Mock

import pytest
from django.core.management.base import CommandError

from apps.github.management.commands import github_sync_contributions as module


@pytest.fixture
def setup_command(mocker):
    repository = Mock(path="OWASP/Nest", node_id="repository")
    query = mocker.patch.object(module, "get_contribution_repositories").return_value
    selected = query.select_related.return_value.order_by.return_value
    selected.__getitem__ = Mock(return_value=[repository])
    selected.filter.return_value = selected
    client = mocker.patch.object(module, "get_github_client").return_value
    client.get_repo.return_value.node_id = repository.node_id
    commits = mocker.patch.object(module, "sync_repository_commits")
    issues = mocker.patch.object(module, "sync_repository_issues")
    pulls = mocker.patch.object(module, "sync_repository_pull_requests")
    options = {
        "repository": None,
        "organization": None,
        "all_repositories": True,
        "days": None,
        "since": None,
        "types": ["commits"],
        "force": False,
        "offset": 0,
        "limit": 25,
    }
    return module.Command(), options, client, commits, issues, pulls


def test_selected_type_uses_shared_collector_and_closes_client(setup_command):
    command, options, client, commits, issues, pulls = setup_command
    command.handle(**options)
    commits.assert_called_once()
    assert commits.call_args.kwargs["force"] is False
    issues.assert_not_called()
    pulls.assert_not_called()
    client.close.assert_called_once()


def test_failure_is_sanitized_and_other_types_continue(setup_command, capsys):
    command, options, client, commits, issues, _ = setup_command
    options["types"] = ["commits", "issues"]
    commits.side_effect = RuntimeError("private-response-body")
    with pytest.raises(CommandError, match="incomplete"):
        command.handle(**options)
    issues.assert_called_once()
    assert "private-response-body" not in capsys.readouterr().err
    client.close.assert_called_once()


@pytest.mark.parametrize(
    "changes",
    [
        {"days": 0},
        {"offset": -1},
        {"limit": 0},
        {"since": "bad"},
        {"since": "2026-01-01"},
        {"repository": "invalid"},
    ],
)
def test_invalid_arguments_fail_before_github(setup_command, changes):
    command, options, client, *_ = setup_command
    options.update(changes)
    with pytest.raises(CommandError):
        command.handle(**options)
    client.get_repo.assert_not_called()


def test_refresh_runs_only_after_success(setup_command, mocker):
    command, options, _, commits, *_ = setup_command
    refresh = mocker.patch.object(command, "refresh_activity")
    options["refresh"] = True
    command.handle(**options)
    refresh.assert_called_once()
    assert refresh.call_args.args[1] == commits.call_args.kwargs["start_at"]
    assert refresh.call_args.args[2] == commits.call_args.kwargs["end_at"]


def test_failed_import_does_not_refresh_activity(setup_command, mocker):
    command, options, _, commits, *_ = setup_command
    refresh = mocker.patch.object(command, "refresh_activity")
    options["refresh"] = True
    commits.side_effect = RuntimeError("failure")
    with pytest.raises(CommandError):
        command.handle(**options)
    refresh.assert_not_called()


@pytest.mark.parametrize("disabled", ["repository", "project"])
def test_disabled_issues_are_reported_as_skipped(setup_command, disabled):
    command, options, _, commits, issues, _ = setup_command
    options["types"] = ["commits", "issues"]
    # The selected repository is the second collector argument.
    command.handle(**options)
    repository = commits.call_args.args[1]
    if disabled == "repository":
        repository.track_issues = False
    else:
        repository.project.track_issues = False
    issues.reset_mock()
    command.stdout = StringIO()
    command.handle(**options)
    issues.assert_not_called()
    output = command.stdout.getvalue()
    assert "issues skipped (tracking disabled)" in output
    assert "issues completed" not in output
