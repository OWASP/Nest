from unittest.mock import MagicMock, patch

import pytest

from apps.github.management.commands.github_enrich_issues import Command


@pytest.mark.parametrize(
    ("argument_name", "expected_properties"),
    [
        ("--offset", {"default": 0, "required": False, "type": int}),
        ("--force-update-hint", {"default": False, "required": False, "action": "store_true"}),
        ("--force-update-summary", {"default": False, "required": False, "action": "store_true"}),
        ("--update-hint", {"default": True, "required": False, "action": "store_true"}),
        ("--update-summary", {"default": True, "required": False, "action": "store_true"}),
    ],
)
def test_add_arguments(argument_name, expected_properties):
    mock_parser = MagicMock()
    command = Command()
    command.add_arguments(mock_parser)
    mock_parser.add_argument.assert_any_call(argument_name, **expected_properties)


@pytest.mark.parametrize(
    ("options", "expected_update_fields", "is_force_update"),
    [
        (
            {
                "force_update_hint": False,
                "force_update_summary": False,
                "update_hint": True,
                "update_summary": True,
                "offset": 0,
            },
            ["hint", "summary"],
            False,
        ),
        (
            {
                "force_update_hint": True,
                "force_update_summary": False,
                "update_hint": True,
                "update_summary": False,
                "offset": 0,
            },
            ["hint"],
            True,
        ),
        (
            {
                "force_update_hint": False,
                "force_update_summary": True,
                "update_hint": False,
                "update_summary": True,
                "offset": 0,
            },
            ["summary"],
            True,
        ),
    ],
)
@patch("apps.github.management.commands.github_enrich_issues.OpenAi")
@patch("apps.github.management.commands.github_enrich_issues.Issue")
def test_handle(
    mock_issue_class, mock_open_ai_class, options, expected_update_fields, is_force_update
):
    mock_open_ai = MagicMock()
    mock_open_ai_class.return_value = mock_open_ai

    mock_issues = [MagicMock(title=f"Test Issue {i}") for i in range(5)]
    for issue in mock_issues:
        issue.generate_hint = MagicMock()
        issue.generate_summary = MagicMock()

    mock_open_issues = MagicMock()

    mock_ordered_queryset = MagicMock()
    mock_ordered_queryset.__iter__.return_value = iter(mock_issues)
    mock_ordered_queryset.count.return_value = len(mock_issues)
    mock_ordered_queryset.__getitem__ = (
        lambda _, idx: mock_issues[idx]
        if isinstance(idx, int)
        else mock_issues[idx.start : idx.stop]
    )

    mock_issue_class.open_issues = mock_open_issues
    if is_force_update:
        mock_open_issues.order_by.return_value = mock_ordered_queryset
    else:
        mock_open_issues.without_summary = mock_open_issues
        mock_open_issues.without_summary.order_by.return_value = mock_ordered_queryset

    command = Command()
    command.handle(**options)

    mock_open_ai_class.assert_called_once()

    if is_force_update:
        mock_open_issues.order_by.assert_called_once_with("-created_at")
    else:
        mock_open_issues.without_summary.order_by.assert_called_once_with("-created_at")

    for issue in mock_issues:
        if "hint" in expected_update_fields:
            issue.generate_hint.assert_called_once_with(open_ai=mock_open_ai)
        else:
            issue.generate_hint.assert_not_called()

        if "summary" in expected_update_fields:
            issue.generate_summary.assert_called_once_with(open_ai=mock_open_ai)
        else:
            issue.generate_summary.assert_not_called()

    mock_issue_class.bulk_save.assert_called_once_with(mock_issues, fields=expected_update_fields)


@patch("apps.github.management.commands.github_enrich_issues.OpenAi")
@patch("apps.github.management.commands.github_enrich_issues.Issue")
def test_handle_with_offset(mock_issue_class, mock_open_ai_class):
    """Test --offset argument handling ensuring command skips specified issues."""
    mock_open_ai = MagicMock()
    mock_open_ai_class.return_value = mock_open_ai

    mock_issues = [MagicMock(title=f"Test Issue {i}") for i in range(5)]
    for issue in mock_issues:
        issue.generate_hint = MagicMock()
        issue.generate_summary = MagicMock()

    mock_open_issues = MagicMock()

    mock_ordered_queryset = MagicMock()
    mock_ordered_queryset.__iter__.return_value = iter(mock_issues)
    mock_ordered_queryset.count.return_value = len(mock_issues)
    mock_ordered_queryset.__getitem__ = (
        lambda _, idx: mock_issues[idx]
        if isinstance(idx, int)
        else mock_issues[idx.start : idx.stop]
    )

    mock_issue_class.open_issues = mock_open_issues
    mock_open_issues.without_summary = mock_open_issues
    mock_open_issues.without_summary.order_by.return_value = mock_ordered_queryset

    command = Command()
    options = {
        "force_update_hint": False,
        "force_update_summary": False,
        "update_hint": True,
        "update_summary": True,
        "offset": 2,
    }
    command.handle(**options)

    for issue in mock_issues[:2]:
        issue.generate_hint.assert_not_called()
        issue.generate_summary.assert_not_called()

    for issue in mock_issues[2:]:
        issue.generate_hint.assert_called_once_with(open_ai=mock_open_ai)
        issue.generate_summary.assert_called_once_with(open_ai=mock_open_ai)

    mock_issue_class.bulk_save.assert_called_once_with(mock_issues[2:], fields=["hint", "summary"])


@patch("apps.github.management.commands.github_enrich_issues.OpenAi")
@patch("apps.github.management.commands.github_enrich_issues.Issue")
def test_handle_with_chunked_save(mock_issue_class, mock_open_ai_class):
    """Tests that the command correctly saves issues in chunks of 1000."""
    mock_open_ai = MagicMock()
    mock_open_ai_class.return_value = mock_open_ai

    mock_issues = [MagicMock(title=f"Test Issue {i}") for i in range(1001)]
    for issue in mock_issues:
        issue.generate_hint = MagicMock()
        issue.generate_summary = MagicMock()

    mock_open_issues = MagicMock()
    mock_issue_class.open_issues = mock_open_issues
    mock_open_issues.without_summary = mock_open_issues

    mock_queryset = MagicMock()
    mock_queryset.count.return_value = len(mock_issues)
    mock_queryset.__getitem__.side_effect = mock_issues.__getitem__
    mock_open_issues.without_summary.order_by.return_value = mock_queryset

    command = Command()
    options = {
        "force_update_hint": False,
        "force_update_summary": False,
        "offset": 0,
        "update_hint": True,
        "update_summary": True,
    }
    command.handle(**options)

    assert mock_issue_class.bulk_save.call_count == 1

    args, kwargs = mock_issue_class.bulk_save.call_args_list[0]
    assert len(args[0]) == 1001
    assert kwargs["fields"] == ["hint", "summary"]


@patch("apps.github.management.commands.github_enrich_issues.OpenAi")
@patch("apps.github.management.commands.github_enrich_issues.Issue")
def test_handle_no_update_fields(mock_issue_class, mock_open_ai_class):
    """Test command handling when no fields are specified for update."""
    mock_open_ai = MagicMock()
    mock_open_ai_class.return_value = mock_open_ai

    mock_issues = [MagicMock(title=f"Test Issue {i}") for i in range(5)]
    for issue in mock_issues:
        issue.generate_hint = MagicMock()
        issue.generate_summary = MagicMock()

    mock_open_issues = MagicMock()

    mock_ordered_queryset = MagicMock()
    mock_ordered_queryset.__iter__.return_value = iter(mock_issues)
    mock_ordered_queryset.count.return_value = len(mock_issues)
    mock_ordered_queryset.__getitem__ = (
        lambda _, idx: mock_issues[idx]
        if isinstance(idx, int)
        else mock_issues[idx.start : idx.stop]
    )

    mock_issue_class.open_issues = mock_open_issues
    mock_open_issues.without_summary = mock_open_issues
    mock_open_issues.without_summary.order_by.return_value = mock_ordered_queryset

    command = Command()
    options = {
        "force_update_hint": False,
        "force_update_summary": False,
        "update_hint": False,
        "update_summary": False,
        "offset": 0,
    }
    command.handle(**options)

    for issue in mock_issues:
        issue.generate_hint.assert_not_called()
        issue.generate_summary.assert_not_called()

    mock_issue_class.bulk_save.assert_called_once_with(mock_issues, fields=[])
