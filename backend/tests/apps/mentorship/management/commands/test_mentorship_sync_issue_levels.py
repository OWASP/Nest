from unittest.mock import MagicMock, patch

import pytest

from apps.mentorship.management.commands.mentorship_sync_issue_levels import Command


@pytest.fixture
def command():
    cmd = Command()
    cmd.stdout = MagicMock()
    cmd.style = MagicMock()
    cmd.style.WARNING = lambda x: x
    cmd.style.SUCCESS = lambda x: x
    return cmd


def make_qs(iterable, exists=True):
    """Helper: return a queryset-like MagicMock that is iterable and supports .exists()."""
    qs = MagicMock(name="QuerySet")
    qs.exists.return_value = exists
    qs.__iter__.return_value = iter(iterable)
    qs.all.return_value = list(iterable)
    return qs


@patch("apps.mentorship.management.commands.mentorship_sync_issue_levels.TaskLevel")
def test_handle_no_task_levels(mock_task_level, command):
    """When no TaskLevel objects exist, command should exit early with a warning."""
    empty_qs = make_qs([], exists=False)
    mock_task_level.objects.select_related.return_value.order_by.return_value = empty_qs

    command.handle()
    command.stdout.write.assert_called_with("No TaskLevel objects found in the database. Exiting.")


@patch("apps.mentorship.management.commands.mentorship_sync_issue_levels.Issue")
@patch("apps.mentorship.management.commands.mentorship_sync_issue_levels.TaskLevel")
def test_handle_updates_issues(mock_task_level, mock_issue, command):
    """When matches exist, issues should be updated and bulk_update called."""
    mock_module = MagicMock()
    mock_module.id = 1
    mock_module.name = "Test Module"

    mock_level_1 = MagicMock(module_id=mock_module.id, name="Beginner", labels=["label-a"])
    mock_level_2 = MagicMock(module_id=mock_module.id, name="Intermediate", labels=["label-b"])

    levels_qs = make_qs([mock_level_1, mock_level_2], exists=True)
    mock_task_level.objects.select_related.return_value.order_by.return_value = levels_qs

    label_a = MagicMock()
    label_a.name = "Label-A"
    label_b = MagicMock()
    label_b.name = "Label-B"
    label_nomatch = MagicMock()
    label_nomatch.name = "No-Match"

    issue_with_label_a = MagicMock()
    issue_with_label_a.labels.all.return_value = [label_a]
    issue_with_label_a.mentorship_modules.all.return_value = [mock_module]
    issue_with_label_a.level = None

    issue_with_label_b = MagicMock()
    issue_with_label_b.labels.all.return_value = [label_b]
    issue_with_label_b.mentorship_modules.all.return_value = [mock_module]
    issue_with_label_b.level = mock_level_1

    issue_no_match = MagicMock()
    issue_no_match.labels.all.return_value = [label_nomatch]
    issue_no_match.mentorship_modules.all.return_value = [mock_module]
    issue_no_match.level = mock_level_1

    issue_already_up_to_date = MagicMock()
    issue_already_up_to_date.labels.all.return_value = [label_a]
    issue_already_up_to_date.mentorship_modules.all.return_value = [mock_module]
    issue_already_up_to_date.level = mock_level_1

    issues_qs = make_qs(
        [issue_with_label_a, issue_with_label_b, issue_no_match, issue_already_up_to_date],
        exists=True,
    )
    mock_issue.objects.prefetch_related.return_value.select_related.return_value = issues_qs

    command.handle()

    assert issue_with_label_a.level == mock_level_1
    assert issue_with_label_b.level == mock_level_2
    assert issue_no_match.level is None
    assert issue_already_up_to_date.level == mock_level_1

    expected_updated = [issue_with_label_a, issue_with_label_b, issue_no_match]
    mock_issue.objects.bulk_update.assert_called_once_with(expected_updated, ["level"])
    command.stdout.write.assert_any_call("Successfully updated the level for 3 issues.")


@patch("apps.mentorship.management.commands.mentorship_sync_issue_levels.Issue")
@patch("apps.mentorship.management.commands.mentorship_sync_issue_levels.TaskLevel")
def test_handle_no_updates_needed(mock_task_level, mock_issue, command):
    """When all issues already have the correct level, bulk_update is not called."""
    mock_module = MagicMock()
    mock_module.id = 1

    mock_level_1 = MagicMock(module_id=mock_module.id, name="Beginner", labels=["label-a"])
    levels_qs = make_qs([mock_level_1], exists=True)
    mock_task_level.objects.select_related.return_value.order_by.return_value = levels_qs

    label_a = MagicMock()
    label_a.name = "Label-A"

    issue_already_up_to_date = MagicMock()
    issue_already_up_to_date.labels.all.return_value = [label_a]
    issue_already_up_to_date.mentorship_modules.all.return_value = [mock_module]
    issue_already_up_to_date.level = mock_level_1

    issues_qs = make_qs([issue_already_up_to_date], exists=True)
    mock_issue.objects.prefetch_related.return_value.select_related.return_value = issues_qs

    command.handle()

    mock_issue.objects.bulk_update.assert_not_called()
    command.stdout.write.assert_any_call("All issue levels are already up-to-date.")
