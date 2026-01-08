from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
import strawberry

from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum
from apps.mentorship.api.internal.nodes.module import (
    CreateModuleInput,
    ModuleNode,
    UpdateModuleInput,
)


class FakeModuleNode:
    """Minimal ModuleNode-like object for testing."""

    def __init__(self):
        self.id = strawberry.ID("1")
        self.key = "test-module"
        self.name = "Test Module"
        self.description = "A test mentorship module."
        self.domains = ["web", "mobile"]
        self.ended_at = datetime(2025, 12, 31, tzinfo=UTC)
        self.experience_level = ExperienceLevelEnum.INTERMEDIATE
        self.labels = ["django", "react"]
        self.program = MagicMock()
        self.program.id = strawberry.ID("program-1")
        self.program.key = "test-program"
        self.project_id = strawberry.ID("project-1")
        self.started_at = datetime(2025, 1, 1, tzinfo=UTC)
        self.tags = ["backend", "frontend"]

        self.mentors = MagicMock()
        self.menteemodule_set = MagicMock()
        self.issues = MagicMock()
        self.project = MagicMock()
        self.project.name = "Test Project"

    def mock_mentors(self):
        return ModuleNode.mentors(self)  # type: ignore[call-arg, arg-type]

    def mock_mentees(self):
        return ModuleNode.mentees(self)  # type: ignore[call-arg, arg-type]

    def mock_issue_mentees(self, issue_number: int):
        return ModuleNode.issue_mentees(self, issue_number)  # type: ignore[call-arg, arg-type]

    def mock_project_name(self):
        return ModuleNode.project_name(self)  # type: ignore[call-arg, arg-type]

    def mock_issues(self, limit: int = 20, offset: int = 0, label: str | None = None):
        return ModuleNode.issues(self, limit, offset, label)  # type: ignore[call-arg, arg-type]

    def mock_issues_count(self, label: str | None = None):
        return ModuleNode.issues_count(self, label)  # type: ignore[call-arg, arg-type]

    def mock_available_labels(self):
        return ModuleNode.available_labels(self)  # type: ignore[call-arg, arg-type]

    def mock_issue_by_number(self, number: int):
        return ModuleNode.issue_by_number(self, number)  # type: ignore[call-arg, arg-type]

    def mock_interested_users(self, issue_number: int):
        return ModuleNode.interested_users(self, issue_number)  # type: ignore[call-arg, arg-type]

    def mock_task_deadline(self, issue_number: int):
        return ModuleNode.task_deadline(self, issue_number)  # type: ignore[call-arg, arg-type]

    def mock_task_assigned_at(self, issue_number: int):
        return ModuleNode.task_assigned_at(self, issue_number)  # type: ignore[call-arg, arg-type]


@pytest.fixture
def mock_module_node():
    """Fixture for a mock ModuleNode instance."""
    m = FakeModuleNode()

    m.mentors.all.return_value = [MagicMock(), MagicMock()]
    m.menteemodule_set.select_related.return_value.filter.return_value.values_list.return_value = [
        "github_user_id_1",
        "github_user_id_2",
    ]
    m.issues.filter.return_value.values_list.return_value = ["issue_id_1"]
    mocked_query_prefetch = m.issues.select_related.return_value.prefetch_related.return_value
    mocked_query_prefetch.filter.return_value.order_by.return_value = [MagicMock()]
    m.issues.count.return_value = 5
    mocked_query_prefetch = m.issues.select_related.return_value.prefetch_related.return_value
    mocked_query_prefetch.filter.return_value.first.return_value = MagicMock()

    return m


def test_module_node_fields(mock_module_node):
    """Test that ModuleNode fields are correctly assigned."""
    assert mock_module_node.id == "1"
    assert mock_module_node.key == "test-module"
    assert mock_module_node.name == "Test Module"
    assert mock_module_node.description == "A test mentorship module."
    assert mock_module_node.domains == ["web", "mobile"]
    assert mock_module_node.ended_at == datetime(2025, 12, 31, tzinfo=UTC)
    assert mock_module_node.experience_level == ExperienceLevelEnum.INTERMEDIATE
    assert mock_module_node.labels == ["django", "react"]
    assert str(mock_module_node.program.id) == "program-1"
    assert mock_module_node.program.key == "test-program"
    assert str(mock_module_node.project_id) == "project-1"
    assert mock_module_node.started_at == datetime(2025, 1, 1, tzinfo=UTC)
    assert mock_module_node.tags == ["backend", "frontend"]


def test_module_node_mentors(mock_module_node):
    """Test the mentors resolver."""
    mentors = mock_module_node.mock_mentors()
    assert len(mentors) == 2
    mock_module_node.mentors.all.assert_called_once()


def test_module_node_mentees(mock_module_node):
    """Test the mentees resolver."""
    with patch("apps.github.models.user.User.objects") as mock_user_objects:
        mock_user_objects.filter.return_value.order_by.return_value = [MagicMock(), MagicMock()]

        mentees = mock_module_node.mock_mentees()
        assert len(mentees) == 2
        mock_module_node.menteemodule_set.select_related.assert_called_once_with(
            "mentee__github_user"
        )
        mock_user_objects.filter.assert_called_once_with(
            id__in=["github_user_id_1", "github_user_id_2"]
        )
        mock_user_objects.filter.return_value.order_by.assert_called_once_with("login")


def test_module_node_issue_mentees(mock_module_node):
    """Test the issue_mentees resolver."""
    with (
        patch("apps.mentorship.models.task.Task.objects") as mock_task_objects,
        patch("apps.github.models.user.User.objects") as mock_user_objects,
    ):
        mock_task_filter_related = (
            mock_task_objects.filter.return_value.select_related.return_value
        )
        mock_task_filter_related.values_list.return_value.distinct.return_value = ["assignee_id_1"]
        mock_user_objects.filter.return_value.order_by.return_value = [MagicMock()]

        mentees = mock_module_node.mock_issue_mentees(issue_number=123)
        assert len(mentees) == 1
        mock_module_node.issues.filter.assert_called_once_with(number=123)
        mock_task_objects.filter.assert_called_once_with(
            module=mock_module_node, issue_id__in=["issue_id_1"], assignee__isnull=False
        )
        mock_user_objects.filter.assert_called_once_with(id__in=["assignee_id_1"])
        mock_user_objects.filter.return_value.order_by.assert_called_once_with("login")


def test_module_node_issue_mentees_no_issue(mock_module_node):
    """Test issue_mentees when no issue is found."""
    mock_module_node.issues.filter.return_value.values_list.return_value = []
    mentees = mock_module_node.mock_issue_mentees(issue_number=123)
    assert mentees == []


def test_module_node_project_name(mock_module_node):
    """Test the project_name resolver."""
    assert mock_module_node.mock_project_name() == "Test Project"


def test_module_node_project_name_no_project():
    """Test project_name when no project is associated."""
    mock = FakeModuleNode()
    mock.project = None
    assert mock.mock_project_name() is None


def test_module_node_issues_with_label(mock_module_node):
    """Test the issues resolver with a label filter."""
    issues_list = mock_module_node.mock_issues(label="bug")
    assert len(issues_list) == 1
    mock_module_node_qs_related = mock_module_node.issues.select_related.return_value
    mock_module_node_qs_related.prefetch_related.return_value.filter.assert_called_once_with(
        labels__name="bug"
    )


def test_module_node_issues_count(mock_module_node):
    """Test the issues_count resolver."""
    count = mock_module_node.mock_issues_count()
    assert count == 5
    mock_module_node.issues.count.assert_called_once()


def test_module_node_issues_count_with_label(mock_module_node):
    """Test issues_count with a label filter."""
    mock_module_node.issues.filter.return_value.count.return_value = 2
    count = mock_module_node.mock_issues_count(label="feature")
    assert count == 2
    mock_module_node.issues.filter.assert_called_once_with(labels__name="feature")


def test_module_node_available_labels(mock_module_node):
    """Test the available_labels resolver."""
    with patch("apps.github.models.Label.objects") as mock_label_objects:
        mock_label_objects.filter.return_value.values_list.return_value.distinct.return_value = [
            "label1",
            "label2",
        ]

        labels = mock_module_node.mock_available_labels()
        assert labels == ["label1", "label2"]
        mock_label_objects.filter.assert_called_once_with(
            issue__mentorship_modules=mock_module_node
        )


def test_module_node_issue_by_number(mock_module_node):
    """Test the issue_by_number resolver."""
    issue = mock_module_node.mock_issue_by_number(number=456)
    assert issue is not None
    mock_module_node.issues.select_related.assert_called_once_with("repository", "author")
    mock_module_node.issues.select_related.return_value.prefetch_related.assert_called_once_with(
        "assignees", "labels"
    )
    mock_module_node_qs_related = mock_module_node.issues.select_related.return_value
    mock_module_node_qs_related.prefetch_related.return_value.filter.assert_called_once_with(
        number=456
    )
    mock_node_related = mock_module_node.issues.select_related.return_value
    mock_node_related.prefetch_related.return_value.filter.return_value.first.assert_called_once()


def test_module_node_interested_users(mock_module_node):
    """Test the interested_users resolver."""
    with patch(
        "apps.mentorship.models.issue_user_interest.IssueUserInterest.objects"
    ) as mock_issue_user_interest_objects:
        mock_interest1 = MagicMock()
        mock_interest1.user = MagicMock(login="user1")
        mock_interest2 = MagicMock()
        mock_interest2.user = MagicMock(login="user2")
        mock_user_interests = mock_issue_user_interest_objects.select_related.return_value
        mock_user_interests.filter.return_value.order_by.return_value = [
            mock_interest1,
            mock_interest2,
        ]

        users = mock_module_node.mock_interested_users(issue_number=789)
        assert len(users) == 2
        assert users[0].login == "user1"
        assert users[1].login == "user2"
        mock_module_node.issues.filter.assert_called_once_with(number=789)
        mock_issue_user_interest_objects.select_related.assert_called_once_with("user")
        mock_issue_user_interest_objects.select_related.return_value.filter.assert_called_once_with(
            module=mock_module_node, issue_id__in=["issue_id_1"]
        )


def test_module_node_interested_users_no_issue(mock_module_node):
    """Test interested_users when no issue is found."""
    mock_module_node.issues.filter.return_value.values_list.return_value = []
    users = mock_module_node.mock_interested_users(issue_number=789)
    assert users == []


def test_module_node_task_deadline(mock_module_node):
    """Test task_deadline method."""
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_order_by = mock_task_objects.filter.return_value.order_by.return_value
        mock_task_order_by.values_list.return_value.first.return_value = datetime(
            2025, 10, 26, tzinfo=UTC
        )

        deadline = mock_module_node.mock_task_deadline(issue_number=101)
        assert deadline == datetime(2025, 10, 26, tzinfo=UTC)
        mock_task_objects.filter.assert_called_once_with(
            module=mock_module_node, issue__number=101, deadline_at__isnull=False
        )


def test_module_node_task_deadline_none(mock_module_node):
    """Test task_deadline when no deadline is found."""
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_order_by = mock_task_objects.filter.return_value.order_by
        mock_task_order_by.return_value.values_list.return_value.first.return_value = None

        deadline = mock_module_node.mock_task_deadline(issue_number=101)
        assert deadline is None


def test_module_node_task_assigned_at(mock_module_node):
    """Test task_assigned_at method."""
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_order_by = mock_task_objects.filter.return_value.order_by
        mock_task_order_by.return_value.values_list.return_value.first.return_value = datetime(
            2025, 9, 15, tzinfo=UTC
        )

        assigned_at = mock_module_node.mock_task_assigned_at(issue_number=202)
        assert assigned_at == datetime(2025, 9, 15, tzinfo=UTC)
        mock_task_objects.filter.assert_called_once_with(
            module=mock_module_node, issue__number=202, assigned_at__isnull=False
        )


def test_module_node_task_assigned_at_none(mock_module_node):
    """Test task_assigned_at when no assignment timestamp is found."""
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_order_by = mock_task_objects.filter.return_value.order_by.return_value
        mock_task_order_by.values_list.return_value.first.return_value = None

        assigned_at = mock_module_node.mock_task_assigned_at(issue_number=202)
        assert assigned_at is None


def test_create_update_input_defaults():
    create_input = CreateModuleInput(
        name="Test",
        description="Desc",
        ended_at=datetime.now(UTC),
        experience_level=ExperienceLevelEnum.BEGINNER,
        program_key="key",
        project_name="Project",
        project_id="id",
        started_at=datetime.now(UTC),
    )
    assert create_input.domains == []
    assert create_input.labels == []
    assert create_input.tags == []

    update_input = UpdateModuleInput(
        key="test-key",
        program_key="key",
        name="Test",
        description="Desc",
        ended_at=datetime.now(UTC),
        experience_level=ExperienceLevelEnum.BEGINNER,
        project_id="id",
        project_name="Project",
        started_at=datetime.now(UTC),
    )
    assert update_input.domains == []
    assert update_input.labels == []
    assert update_input.tags == []
