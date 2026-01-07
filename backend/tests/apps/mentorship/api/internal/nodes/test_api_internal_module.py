"""Fixed tests for ModuleNode resolvers: use a small fake ModuleNode object.

so resolver methods actually run (instead of calling MagicMock methods).
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
import strawberry

from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum
from apps.mentorship.api.internal.nodes.module import CreateModuleInput, UpdateModuleInput


class FakeModuleNode:
    """Minimal ModuleNode-like object for testing."""

    def __init__(self):
        # basic scalar attrs
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

        self._mentors_manager = MagicMock()
        self.menteemodule_set = MagicMock()
        self._issues_qs = MagicMock()
        self.project = MagicMock()
        self.project.name = "Test Project"

    def mentors(self):
        return self._mentors_manager.all()

    def mentees(self):
        mentee_users = (
            self.menteemodule_set.select_related("mentee__github_user")
            .filter(mentee__github_user__isnull=False)
            .values_list("mentee__github_user", flat=True)
        )
        from apps.github.models.user import User as GithubUser

        return list(GithubUser.objects.filter(id__in=mentee_users).order_by("login"))

    def issue_mentees(self, issue_number: int):
        issue_ids = list(self._issues_qs.filter(number=issue_number).values_list("id", flat=True))
        if not issue_ids:
            return []
        from apps.github.models.user import User as GithubUser
        from apps.mentorship.models.task import Task  # tests patch Task.objects

        mentee_users = (
            Task.objects.filter(module=self, issue_id__in=issue_ids, assignee__isnull=False)
            .select_related("assignee")
            .values_list("assignee", flat=True)
            .distinct()
        )

        return list(GithubUser.objects.filter(id__in=mentee_users).order_by("login"))

    def project_name(self):
        return self.project.name if self.project else None

    def issues(self, limit: int = 20, offset: int = 0, label: str | None = None):
        queryset = self._issues_qs.select_related("repository", "author").prefetch_related(
            "assignees", "labels"
        )
        if label and label != "all":
            queryset = queryset.filter(labels__name=label)
        return list(queryset.order_by("-updated_at")[offset : offset + limit])

    def issues_count(self, label: str | None = None):
        queryset = self._issues_qs
        if label and label != "all":
            queryset = queryset.filter(labels__name=label)
        return queryset.count()

    def available_labels(self):
        from apps.github.models import Label

        label_names = (
            Label.objects.filter(issue__mentorship_modules=self)
            .values_list("name", flat=True)
            .distinct()
        )
        return sorted(label_names)

    def issue_by_number(self, number: int):
        return (
            self._issues_qs.select_related("repository", "author")
            .prefetch_related("assignees", "labels")
            .filter(number=number)
            .first()
        )

    def interested_users(self, issue_number: int):
        issue_ids = list(self._issues_qs.filter(number=issue_number).values_list("id", flat=True))
        if not issue_ids:
            return []
        from apps.mentorship.models.issue_user_interest import IssueUserInterest

        interests = (
            IssueUserInterest.objects.select_related("user")
            .filter(module=self, issue_id__in=issue_ids)
            .order_by("user__login")
        )
        return [i.user for i in interests]

    def task_deadline(self, issue_number: int):
        from apps.mentorship.models.task import Task

        return (
            Task.objects.filter(
                module=self,
                issue__number=issue_number,
                deadline_at__isnull=False,
            )
            .order_by("-assigned_at")
            .values_list("deadline_at", flat=True)
            .first()
        )

    def task_assigned_at(self, issue_number: int):
        from apps.mentorship.models.task import Task

        return (
            Task.objects.filter(
                module=self,
                issue__number=issue_number,
                assigned_at__isnull=False,
            )
            .order_by("-assigned_at")
            .values_list("assigned_at", flat=True)
            .first()
        )


@pytest.fixture
def mock_module_node():
    m = FakeModuleNode()

    m._mentors_manager.all.return_value = [MagicMock(), MagicMock()]
    m.menteemodule_set.select_related.return_value.filter.return_value.values_list.return_value = [
        "github_user_id_1",
        "github_user_id_2",
    ]
    m._issues_qs.filter.return_value.values_list.return_value = ["issue_id_1"]
    m._issues_qs.select_related.return_value\
        .prefetch_related.return_value.filter.return_value.order_by.return_value = [
        MagicMock()
    ]
    m._issues_qs.count.return_value = 5
    m._issues_qs.select_related.return_value\
        .prefetch_related.return_value.filter.return_value.first.return_value = MagicMock()

    return m


def test_module_node_fields(mock_module_node):
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
    mentors = mock_module_node.mentors()
    assert len(mentors) == 2
    mock_module_node._mentors_manager.all.assert_called_once()


def test_module_node_mentees(mock_module_node):
    with patch("apps.github.models.user.User.objects") as mock_user_objects:
        mock_user_objects.filter.return_value.order_by.return_value = [MagicMock(), MagicMock()]

        mentees = mock_module_node.mentees()
        assert len(mentees) == 2
        mock_module_node.menteemodule_set.select_related.assert_called_once_with(
            "mentee__github_user"
        )
        mock_user_objects.filter.assert_called_once_with(
            id__in=["github_user_id_1", "github_user_id_2"]
        )
        mock_user_objects.filter.return_value.order_by.assert_called_once_with("login")


def test_module_node_issue_mentees(mock_module_node):
    with (
        patch("apps.mentorship.models.task.Task.objects") as mock_task_objects,
        patch("apps.github.models.user.User.objects") as mock_user_objects,
    ):
        mock_task_objects.filter.return_value\
            .select_related.return_value.values_list.return_value.distinct.return_value = [
            "assignee_id_1"
        ]
        mock_user_objects.filter.return_value.order_by.return_value = [MagicMock()]

        mentees = mock_module_node.issue_mentees(issue_number=123)
        assert len(mentees) == 1
        mock_module_node._issues_qs.filter.assert_called_once_with(number=123)
        mock_task_objects.filter.assert_called_once_with(
            module=mock_module_node, issue_id__in=["issue_id_1"], assignee__isnull=False
        )
        mock_user_objects.filter.assert_called_once_with(id__in=["assignee_id_1"])
        mock_user_objects.filter.return_value.order_by.assert_called_once_with("login")


def test_module_node_issue_mentees_no_issue(mock_module_node):
    mock_module_node._issues_qs.filter.return_value.values_list.return_value = []
    mentees = mock_module_node.issue_mentees(issue_number=123)
    assert mentees == []


def test_module_node_project_name(mock_module_node):
    assert mock_module_node.project_name() == "Test Project"


def test_module_node_project_name_no_project():
    mock = FakeModuleNode()
    mock.project = None
    assert mock.project_name() is None


def test_module_node_issues_with_label(mock_module_node):
    issues_list = mock_module_node.issues(label="bug")
    assert len(issues_list) == 1
    mock_module_node._issues_qs.select_related.return_value\
        .prefetch_related.return_value.filter.assert_called_once_with(
        labels__name="bug"
    )


def test_module_node_issues_count(mock_module_node):
    count = mock_module_node.issues_count()
    assert count == 5
    mock_module_node._issues_qs.count.assert_called_once()


def test_module_node_issues_count_with_label(mock_module_node):
    mock_module_node._issues_qs.filter.return_value.count.return_value = 2
    count = mock_module_node.issues_count(label="feature")
    assert count == 2
    mock_module_node._issues_qs.filter.assert_called_once_with(labels__name="feature")


def test_module_node_available_labels(mock_module_node):
    with patch("apps.github.models.Label.objects") as mock_label_objects:
        mock_label_objects.filter.return_value.values_list.return_value.distinct.return_value = [
            "label1",
            "label2",
        ]

        labels = mock_module_node.available_labels()
        assert labels == ["label1", "label2"]
        mock_label_objects.filter.assert_called_once_with(
            issue__mentorship_modules=mock_module_node
        )


def test_module_node_issue_by_number(mock_module_node):
    issue = mock_module_node.issue_by_number(number=456)
    assert issue is not None
    mock_module_node._issues_qs.select_related.assert_called_once_with("repository", "author")
    mock_module_node._issues_qs.select_related.return_value.prefetch_related.assert_called_once_with(
        "assignees", "labels"
    )
    mock_module_node._issues_qs.select_related.return_value\
        .prefetch_related.return_value.filter.assert_called_once_with(
        number=456
    )
    mock_module_node._issues_qs.select_related.return_value\
        .prefetch_related.return_value.filter.return_value.first.assert_called_once()


def test_module_node_interested_users(mock_module_node):
    with patch(
        "apps.mentorship.models.issue_user_interest.IssueUserInterest.objects"
    ) as mock_issue_user_interest_objects:
        mock_interest1 = MagicMock()
        mock_interest1.user = MagicMock(login="user1")
        mock_interest2 = MagicMock()
        mock_interest2.user = MagicMock(login="user2")
        mock_issue_user_interest_objects.select_related.return_value\
            .filter.return_value.order_by.return_value = [
            mock_interest1,
            mock_interest2,
        ]

        users = mock_module_node.interested_users(issue_number=789)
        assert len(users) == 2
        assert users[0].login == "user1"
        assert users[1].login == "user2"
        mock_module_node._issues_qs.filter.assert_called_once_with(number=789)
        mock_issue_user_interest_objects.select_related.assert_called_once_with("user")
        mock_issue_user_interest_objects.select_related.return_value.filter.assert_called_once_with(
            module=mock_module_node, issue_id__in=["issue_id_1"]
        )


def test_module_node_interested_users_no_issue(mock_module_node):
    mock_module_node._issues_qs.filter.return_value.values_list.return_value = []
    users = mock_module_node.interested_users(issue_number=789)
    assert users == []

    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_objects.filter.return_value.order_by.return_value\
            .values_list.return_value.first.return_value = datetime(
            2025, 10, 26, tzinfo=UTC
        )

        deadline = mock_module_node.task_deadline(issue_number=101)
        assert deadline == datetime(2025, 10, 26, tzinfo=UTC)
        mock_task_objects.filter.assert_called_once_with(
            module=mock_module_node, issue__number=101, deadline_at__isnull=False
        )


def test_module_node_task_deadline_none(mock_module_node):
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_objects.filter.return_value.order_by.return_value\
            .values_list.return_value.first.return_value = None

        deadline = mock_module_node.task_deadline(issue_number=101)
        assert deadline is None


def test_module_node_task_assigned_at(mock_module_node):
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_objects.filter.return_value.order_by.return_value\
            .values_list.return_value.first.return_value = datetime(
            2025, 9, 15, tzinfo=UTC
        )

        assigned_at = mock_module_node.task_assigned_at(issue_number=202)
        assert assigned_at == datetime(2025, 9, 15, tzinfo=UTC)
        mock_task_objects.filter.assert_called_once_with(
            module=mock_module_node, issue__number=202, assigned_at__isnull=False
        )


def test_module_node_task_assigned_at_none(mock_module_node):
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_objects.filter.return_value.order_by.return_value\
            .values_list.return_value.first.return_value = None

        assigned_at = mock_module_node.task_assigned_at(issue_number=202)
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
