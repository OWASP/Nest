from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from apps.mentorship.management.commands.mentorship_update_comments import (
    Command,
)


def make_qs(iterable, exist):
    """Return a queryset-like MagicMock that is iterable."""
    qs = MagicMock(name="QuerySet")
    items = list(iterable)
    qs.exists.return_value = exist
    qs.__iter__.return_value = iter(items)
    qs.all.return_value = items
    qs.count.return_value = len(items)
    qs.distinct.return_value = qs
    return qs


def make_user(user_id, login):
    user = MagicMock()
    user.id = user_id
    user.login = login
    return user


def make_comment(body, author, created_at=None):
    c = MagicMock()
    c.body = body
    c.author = author
    c.nest_created_at = created_at or "now"
    return c


@pytest.fixture
def command():
    cmd = Command()
    cmd.stdout = MagicMock()
    cmd.style = MagicMock()
    cmd.style.WARNING = lambda x: x
    cmd.style.SUCCESS = lambda x: x
    cmd.style.ERROR = lambda x: x
    return cmd


def test_handle_calls_process_mentorship_modules(command):
    """Test that handle() calls process_mentorship_modules."""
    with patch.object(command, "process_mentorship_modules") as mock_process:
        command.handle()
        mock_process.assert_called_once()


@pytest.fixture
def mock_module():
    m = MagicMock()
    m.name = "Test Module"
    vlist_qs = make_qs([1, 2], exist=True)
    m.project.repositories.filter.return_value.values_list.return_value.distinct.return_value = (
        vlist_qs
    )
    return m


@pytest.fixture
def mock_issue():
    issue = MagicMock()
    issue.number = 123
    issue.title = "Test Issue Title"
    empty_comments_qs = make_qs([], exist=False)
    issue.comments.select_related.return_value.filter.return_value.order_by.return_value = (
        empty_comments_qs
    )
    return issue


@patch("apps.mentorship.management.commands.mentorship_update_comments.Module")
def test_process_mentorship_modules_no_published_modules(mock_module, command):
    """Test process_mentorship_modules when no published modules exist."""
    mock_module.published_modules.all.return_value.exists.return_value = False
    command.process_mentorship_modules()
    command.stdout.write.assert_called_with("No published mentorship modules found. Exiting.")


@patch("apps.mentorship.management.commands.mentorship_update_comments.Module")
def test_process_mentorship_modules_no_modules_with_labels(mock_module, command):
    """Test process_mentorship_modules when no modules with labels exist."""
    mock_module.published_modules.all.return_value.exists.return_value = True
    mock_excluded_modules = mock_module.published_modules.all.return_value.exclude.return_value
    mock_excluded_modules.select_related.return_value.exists.return_value = False
    command.process_mentorship_modules()
    command.stdout.write.assert_called_with(
        "No published mentorship modules with labels found. Exiting."
    )


@patch("apps.mentorship.management.commands.mentorship_update_comments.Module")
def test_process_mentorship_modules_with_modules(mock_module, command):
    """Test process_mentorship_modules with modules that have labels."""
    mock_module.published_modules.all.return_value.exists.return_value = True
    mock_mod = MagicMock()
    mock_mod.name = "Test Module"
    mock_excluded_modules = mock_module.published_modules.all.return_value.exclude.return_value
    mock_excluded_modules.select_related.return_value.exists.return_value = True
    mock_excluded_modules.select_related.return_value.__iter__ = MagicMock(
        return_value=iter([mock_mod])
    )

    with patch.object(command, "process_module") as mock_process:
        command.process_mentorship_modules()
        mock_process.assert_called_once_with(mock_mod)
    command.stdout.write.assert_any_call("Processed successfully!")


@patch("apps.mentorship.management.commands.mentorship_update_comments.get_github_client")
def test_process_module_no_repos(mock_get_gh, command, mock_module):  # noqa: ARG001
    """Test process_module when module has no repositories."""
    repo_chain = mock_module.project.repositories.filter.return_value
    repo_chain.values_list.return_value.distinct.return_value.exists.return_value = False
    command.process_module(mock_module)
    command.stdout.write.assert_any_call("Skipping. Module 'Test Module' has no repositories.")


@patch("apps.mentorship.management.commands.mentorship_update_comments.get_github_client")
@patch("apps.mentorship.management.commands.mentorship_update_comments.sync_issue_comments")
@patch.object(Command, "process_issue_interests")
@patch("apps.mentorship.management.commands.mentorship_update_comments.Issue")
def test_process_module(
    mock_issue_1,
    mock_process_issue_interests,
    mock_sync_issue_comments,
    mock_get_github_client,
    command,
    mock_module,
    mock_issue,
):
    """Test process_module orchestrates issue syncing and interest processing."""
    mock_issue.id = 1
    mock_issue.title = "Test Issue 1"
    mock_issue.number = 123

    issues_qs = make_qs([mock_issue], exist=True)
    mock_issue_1.objects.filter.return_value.distinct.return_value = issues_qs

    author = make_user(1, "login")
    comment = make_comment("body", author, created_at="now")
    comments_qs = make_qs([comment], exist=True)
    mock_issue.comments.select_related.return_value.filter.return_value.order_by.return_value = (
        comments_qs
    )

    command.process_module(mock_module)

    mock_sync_issue_comments.assert_called_once_with(
        mock_get_github_client.return_value, mock_issue
    )
    mock_process_issue_interests.assert_called_once_with(mock_issue, mock_module)


@patch("apps.mentorship.management.commands.mentorship_update_comments.IssueUserInterest")
def test_process_issue_interests_new_interest(
    mock_issue_user_interest, command, mock_issue, mock_module
):
    """Test process_issue_interests correctly registers new interests."""
    user1 = make_user(1, "user1")
    comment1 = make_comment(body="I am /interested", author=user1, created_at="2023-01-01")

    comments_qs = make_qs([comment1], exist=True)
    mock_issue.comments.select_related.return_value.filter.return_value.order_by.return_value = (
        comments_qs
    )

    mock_issue_user_interest.objects.filter.return_value.values_list.return_value = []

    mock_issue_user_interest.side_effect = lambda **kw: SimpleNamespace(
        module=kw.get("module"), issue=kw.get("issue"), user=kw.get("user")
    )
    mock_issue_user_interest.objects.bulk_create = MagicMock()

    command.process_issue_interests(mock_issue, mock_module)

    mock_issue_user_interest.objects.bulk_create.assert_called_once()
    created_interest = mock_issue_user_interest.objects.bulk_create.call_args[0][0][0]
    assert created_interest.module == mock_module
    assert created_interest.issue == mock_issue
    assert created_interest.user == user1
    command.stdout.write.assert_any_call(
        command.style.SUCCESS("Registered 1 new interest(s) for issue #123: user1")
    )


@patch("apps.mentorship.management.commands.mentorship_update_comments.IssueUserInterest")
def test_process_issue_interests_remove_interest(
    mock_issue_user_interest, command, mock_issue, mock_module
):
    """Test process_issue_interests correctly removes interests."""
    user1 = make_user(1, "user1")
    comment1 = make_comment(body="Not interested anymore", author=user1, created_at="2023-01-01")

    comments_qs = make_qs([comment1], exist=True)
    mock_issue.comments.select_related.return_value.filter.return_value.order_by.return_value = (
        comments_qs
    )

    mock_issue_user_interest.objects.filter.return_value.values_list.return_value = [1]
    mock_issue_user_interest.objects.filter.return_value.delete.return_value = (1, {})

    mock_issue_user_interest.side_effect = lambda **kw: SimpleNamespace(
        module=kw.get("module"), issue=kw.get("issue"), user=kw.get("user")
    )
    mock_issue_user_interest.objects.bulk_create = MagicMock()

    command.process_issue_interests(mock_issue, mock_module)

    mock_issue_user_interest.objects.bulk_create.assert_not_called()
    mock_issue_user_interest.objects.filter.assert_any_call(
        module=mock_module, issue=mock_issue, user_id__in=[1]
    )
    mock_issue_user_interest.objects.filter.return_value.delete.assert_called_once()
    command.stdout.write.assert_any_call(
        command.style.WARNING("Unregistered 1 interest(s) for issue #123: user1")
    )


@patch("apps.mentorship.management.commands.mentorship_update_comments.IssueUserInterest")
def test_process_issue_interests_existing_interest_removed(
    mock_issue_user_interest, command, mock_issue, mock_module
):
    """Existing interest should be removed when user no longer shows interest."""
    mock_issue.number = 1

    user1 = make_user(1, "user1")
    comment1 = make_comment(body="Just a regular comment", author=user1, created_at="2023-01-01")

    comments_qs = make_qs([comment1], exist=True)
    mock_issue.comments.select_related.return_value.filter.return_value.order_by.return_value = (
        comments_qs
    )

    mock_issue_user_interest.objects.filter.return_value.values_list.return_value = [1]
    mock_issue_user_interest.objects.filter.return_value.delete.return_value = (1, {})

    mock_issue_user_interest.side_effect = lambda **kw: SimpleNamespace(
        module=kw.get("module"), issue=kw.get("issue"), user=kw.get("user")
    )
    mock_issue_user_interest.objects.bulk_create = MagicMock()

    command.process_issue_interests(mock_issue, mock_module)

    mock_issue_user_interest.objects.bulk_create.assert_not_called()

    mock_issue_user_interest.objects.filter.return_value.delete.assert_called_once()
    command.stdout.write.assert_any_call(
        command.style.WARNING("Unregistered 1 interest(s) for issue #1: user1")
    )


@patch("apps.mentorship.management.commands.mentorship_update_comments.IssueUserInterest")
def test_process_issue_interests_multiple_comments_single_user(
    mock_issue_user_interest, command, mock_issue, mock_module
):
    """Test process_issue_interests with multiple comments from a single user."""
    user1 = make_user(1, "user1")
    comment1 = make_comment(body="Some text", author=user1, created_at="2023-01-01")
    comment2 = make_comment(body="/interested in this", author=user1, created_at="2023-01-02")
    comment3 = make_comment(body="Another comment", author=user1, created_at="2023-01-03")

    comments_qs = make_qs([comment1, comment2, comment3], exist=True)
    mock_issue.comments.select_related.return_value.filter.return_value.order_by.return_value = (
        comments_qs
    )

    mock_issue_user_interest.objects.filter.return_value.values_list.return_value = []

    mock_issue_user_interest.side_effect = lambda **kw: SimpleNamespace(
        module=kw.get("module"), issue=kw.get("issue"), user=kw.get("user")
    )
    mock_issue_user_interest.objects.bulk_create = MagicMock()

    command.process_issue_interests(mock_issue, mock_module)

    mock_issue_user_interest.objects.bulk_create.assert_called_once()
    created_interest = mock_issue_user_interest.objects.bulk_create.call_args[0][0][0]
    assert created_interest.user == user1
    command.stdout.write.assert_any_call(
        command.style.SUCCESS("Registered 1 new interest(s) for issue #123: user1")
    )


@patch("apps.mentorship.management.commands.mentorship_update_comments.IssueUserInterest")
def test_process_issue_interests_multiple_users(
    mock_issue_user_interest, command, mock_issue, mock_module
):
    """Test mixed user interest changes: some created, some removed."""
    mock_issue.number = 123

    user1 = make_user(1, "user1")
    user2 = make_user(2, "user2")
    user3 = make_user(3, "user3")
    comment1_user1 = make_comment(body="not interested", author=user1, created_at="2023-01-01")
    comment2_user2 = make_comment(body="regular comment", author=user2, created_at="2023-01-02")
    comment4_user2 = make_comment(body="/interested", author=user2, created_at="2023-01-04")
    comment3_user3 = make_comment(body="/interested", author=user3, created_at="2023-01-03")

    comments_qs = make_qs(
        [comment1_user1, comment2_user2, comment3_user3, comment4_user2],
        exist=True,
    )
    mock_issue.comments.select_related.return_value.filter.return_value.order_by.return_value = (
        comments_qs
    )
    mock_issue_user_interest.objects.filter.return_value.values_list.return_value = [1]
    mock_issue_user_interest.objects.filter.return_value.delete.return_value = (1, {})

    mock_issue_user_interest.side_effect = lambda **kw: SimpleNamespace(
        module=kw.get("module"), issue=kw.get("issue"), user=kw.get("user")
    )
    mock_issue_user_interest.objects.bulk_create = MagicMock()

    command.process_issue_interests(mock_issue, mock_module)
    assert mock_issue_user_interest.objects.bulk_create.called
    created_lists = mock_issue_user_interest.objects.bulk_create.call_args_list
    created_users = set()
    for call in created_lists:
        for created in call[0][0]:
            created_users.add(created.user.id)
    assert created_users == {2, 3}
    filter_calls = mock_issue_user_interest.objects.filter.call_args_list
    found_user_id_in_call = any(
        ("user_id__in" in c.kwargs and c.kwargs["user_id__in"] == [1]) for c in filter_calls
    )
    assert found_user_id_in_call, (
        f"expected filter(..., user_id__in=[1]) in filter calls: {filter_calls}"
    )
    mock_issue_user_interest.objects.filter.return_value.delete.assert_called_once()

    command.stdout.write.assert_any_call(
        command.style.SUCCESS("Registered 2 new interest(s) for issue #123: user2, user3")
    )
    command.stdout.write.assert_any_call(
        command.style.WARNING("Unregistered 1 interest(s) for issue #123: user1")
    )


@patch("apps.mentorship.management.commands.mentorship_update_comments.IssueUserInterest")
def test_process_issue_interests_no_interest_not_existing(
    mock_issue_user_interest, command, mock_issue, mock_module
):
    """Test loop continues when user is not interested and not in existing interests."""
    user1 = make_user(1, "user1")
    comment1 = make_comment(body="Just a regular comment", author=user1, created_at="2023-01-01")

    comments_qs = make_qs([comment1], exist=True)
    mock_issue.comments.select_related.return_value.filter.return_value.order_by.return_value = (
        comments_qs
    )
    mock_issue_user_interest.objects.filter.return_value.values_list.return_value = []

    mock_issue_user_interest.side_effect = lambda **kw: SimpleNamespace(
        module=kw.get("module"), issue=kw.get("issue"), user=kw.get("user")
    )
    mock_issue_user_interest.objects.bulk_create = MagicMock()

    command.process_issue_interests(mock_issue, mock_module)

    mock_issue_user_interest.objects.bulk_create.assert_not_called()
