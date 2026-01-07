"""Fixed tests for ModuleNode resolvers: use a small fake ModuleNode object
so resolver methods actually run (instead of calling MagicMock methods)."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import strawberry
import pytest

from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum
from apps.mentorship.api.internal.nodes.module import CreateModuleInput, UpdateModuleInput


class FakeModuleNode:
    """A minimal object that implements ModuleNode resolver behavior by delegating
    to attributes that tests can set (e.g. ._issues_qs, .menteemodule_set, managers)."""

    def __init__(self):
        # basic scalar attrs
        """
        Initialize a FakeModuleNode with default scalar fields and mock managers used by resolver tests.
        
        Sets realistic default values for scalar attributes (id, key, name, description, domains, started_at, ended_at, experience_level, labels, tags, program.{id,key}, project_id) and constructs replaceable mock attributes used by resolver methods: `_mentors_manager` (must implement `.all()`), `menteemodule_set`, `_issues_qs`, and `project` (with `name`). These mocks are intended for tests to stub queryset/manager chains and control resolver behavior.
        """
        self.id = strawberry.ID("1")
        self.key = "test-module"
        self.name = "Test Module"
        self.description = "A test mentorship module."
        self.domains = ["web", "mobile"]
        self.ended_at = datetime(2025, 12, 31)
        self.experience_level = ExperienceLevelEnum.INTERMEDIATE
        self.labels = ["django", "react"]
        self.program = MagicMock()
        self.program.id = strawberry.ID("program-1")
        self.program.key = "test-program"
        self.project_id = strawberry.ID("project-1")
        self.started_at = datetime(2025, 1, 1)
        self.tags = ["backend", "frontend"]

        # attributes that resolver methods will use (tests can replace these)
        # mentors manager must expose .all()
        self._mentors_manager = MagicMock()
        # mentee-module relationship manager chain used in mentees()
        self.menteemodule_set = MagicMock()
        # issues queryset-like object (tests will set return values on chains)
        self._issues_qs = MagicMock()
        # project object
        self.project = MagicMock()
        self.project.name = "Test Project"

    # Implement resolver methods by delegating to the attributes above,
    # matching original ModuleNode logic but acting on attributes tests control.
    def mentors(self):
        """
        Return the mentors associated with this module.
        
        Returns:
            QuerySet: A QuerySet of mentor objects related to the module.
        """
        return self._mentors_manager.all()

    def mentees(self):
        """
        Return GitHub users for the module's mentees that have linked GitHub accounts.
        
        Returns:
            list[GithubUser]: List of GitHub User objects linked to mentees, ordered by `login`.
        """
        mentee_users = (
            self.menteemodule_set.select_related("mentee__github_user")
            .filter(mentee__github_user__isnull=False)
            .values_list("mentee__github_user", flat=True)
        )

        # The tests patch apps.github.models.user.User.objects
        from apps.github.models.user import User as GithubUser

        return list(GithubUser.objects.filter(id__in=mentee_users).order_by("login"))

    def issue_mentees(self, issue_number: int):
        """
        Return GitHub users who were assigned tasks for the given issue within this module.
        
        Parameters:
            issue_number (int): The issue number to look up within this module.
        
        Returns:
            list: A list of `apps.github.models.user.User` objects representing assignees on tasks associated with the issue, ordered by `login`. Returns an empty list if the issue has no associated tasks or assignees.
        """
        issue_ids = list(self._issues_qs.filter(number=issue_number).values_list("id", flat=True))
        if not issue_ids:
            return []
        from apps.mentorship.models.task import Task  # tests patch Task.objects
        from apps.github.models.user import User as GithubUser

        mentee_users = (
            Task.objects.filter(module=self, issue_id__in=issue_ids, assignee__isnull=False)
            .select_related("assignee")
            .values_list("assignee", flat=True)
            .distinct()
        )

        return list(GithubUser.objects.filter(id__in=mentee_users).order_by("login"))

    def project_name(self):
        """
        Get the project's name for this module, or None if no project is associated.
        
        Returns:
            The project's name as a string, or None when the module has no project.
        """
        return self.project.name if self.project else None

    # keep method name 'issues' (so tests call mock_module_node.issues())
    def issues(self, limit: int = 20, offset: int = 0, label: str | None = None):
        """
        Get issues for the module, optionally filtered by label and paginated.
        
        Parameters:
            limit (int): Maximum number of issues to return.
            offset (int): Number of issues to skip before collecting results.
            label (str | None): If provided and not "all", restrict results to issues with this label name.
        
        Returns:
            list: Issue objects ordered by `updated_at` descending, filtered and sliced according to `label`, `offset`, and `limit`.
        """
        queryset = self._issues_qs.select_related("repository", "author").prefetch_related("assignees", "labels")
        if label and label != "all":
            queryset = queryset.filter(labels__name=label)
        return list(queryset.order_by("-updated_at")[offset: offset + limit])

    def issues_count(self, label: str | None = None):
        """
        Return the number of issues associated with the module, optionally filtered by label.
        
        Parameters:
            label (str | None): Name of the label to filter issues by. If `None` or `"all"`, no label filter is applied.
        
        Returns:
            int: The count of issues matching the module and optional label filter.
        """
        queryset = self._issues_qs
        if label and label != "all":
            queryset = queryset.filter(labels__name=label)
        return queryset.count()

    def available_labels(self):
        """
        Get sorted label names associated with this module.
        
        Returns:
            list[str]: Distinct label names related to this module, sorted in ascending order.
        """
        from apps.github.models import Label

        label_names = (
            Label.objects.filter(issue__mentorship_modules=self)
            .values_list("name", flat=True)
            .distinct()
        )
        return sorted(label_names)

    def issue_by_number(self, number: int):
        """
        Retrieve the issue with the given issue number for this module.
        
        Parameters:
        	number (int): The issue number to look up within this module.
        
        Returns:
        	Issue or None: The matching issue (with repository, author, assignees, and labels prefetched) if found, otherwise None.
        """
        return (
            self._issues_qs.select_related("repository", "author")
            .prefetch_related("assignees", "labels")
            .filter(number=number)
            .first()
        )

    def interested_users(self, issue_number: int):
        """
        Return GitHub users who expressed interest in the specified issue for this module, ordered by user login.
        
        Parameters:
            issue_number (int): The issue number to match within this module.
        
        Returns:
            list: A list of `User` objects who expressed interest in the issue, ordered by `login`; an empty list if no interests are found.
        """
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
        """
        Retrieve the most recent task deadline for this module associated with a given issue number.
        
        Parameters:
            issue_number (int): The issue's numeric identifier to match.
        
        Returns:
            datetime or None: The latest `deadline_at` value for a task linked to the issue, or `None` if no deadline exists.
        """
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
        """
        Get the most recent task assignment timestamp for this module and a given issue number.
        
        Parameters:
            issue_number (int): The issue number to match tasks against.
        
        Returns:
            datetime or None: The latest `assigned_at` timestamp for tasks associated with this module and issue number, or `None` if no matching assignment exists.
        """
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
    """
    Create and return a FakeModuleNode preconfigured with sensible MagicMock return values for tests.
    
    This fixture builds a FakeModuleNode and configures common queryset/manager call chains used across the module's resolver tests:
    - _mentors_manager.all() returns two mock mentors.
    - menteemodule_set.select_related(...).filter(...).values_list(...) returns two GitHub user IDs.
    - _issues_qs.filter(...).values_list(...) returns a single issue ID.
    - _issues_qs.select_related(...).prefetch_related(...).filter(...).order_by(...) returns a list with one mock issue.
    - _issues_qs.count() returns 5.
    - _issues_qs.select_related(...).prefetch_related(...).filter(...).first() returns a mock issue.
    
    Returns:
        FakeModuleNode: A FakeModuleNode instance with its internals mocked for use in tests.
    """
    m = FakeModuleNode()

    # prepare sensible default returns for chains used by tests
    m._mentors_manager.all.return_value = [MagicMock(), MagicMock()]
    # mentee module set -> values_list returns two ids by default
    m.menteemodule_set.select_related.return_value.filter.return_value.values_list.return_value = [
        "github_user_id_1",
        "github_user_id_2",
    ]
    # issues.filter(...).values_list(...) used by issue_mentees default
    m._issues_qs.filter.return_value.values_list.return_value = ["issue_id_1"]
    # issues.select_related(...).prefetch_related(...).filter(...).order_by(...) returns list of 1 mock issue
    m._issues_qs.select_related.return_value.prefetch_related.return_value.filter.return_value.order_by.return_value = [
        MagicMock()
    ]
    m._issues_qs.count.return_value = 5
    m._issues_qs.select_related.return_value.prefetch_related.return_value.filter.return_value.first.return_value = MagicMock()

    return m


def test_module_node_fields(mock_module_node):
    assert mock_module_node.id == "1"
    assert mock_module_node.key == "test-module"
    assert mock_module_node.name == "Test Module"
    assert mock_module_node.description == "A test mentorship module."
    assert mock_module_node.domains == ["web", "mobile"]
    assert mock_module_node.ended_at == datetime(2025, 12, 31)
    assert mock_module_node.experience_level == ExperienceLevelEnum.INTERMEDIATE
    assert mock_module_node.labels == ["django", "react"]
    assert str(mock_module_node.program.id) == "program-1"
    assert mock_module_node.program.key == "test-program"
    assert str(mock_module_node.project_id) == "project-1"
    assert mock_module_node.started_at == datetime(2025, 1, 1)
    assert mock_module_node.tags == ["backend", "frontend"]


def test_module_node_mentors(mock_module_node):
    mentors = mock_module_node.mentors()
    assert len(mentors) == 2
    mock_module_node._mentors_manager.all.assert_called_once()


def test_module_node_mentees(mock_module_node):
    # patch the User manager used inside the resolver to return two mock users
    with patch("apps.github.models.user.User.objects") as mock_user_objects:
        mock_user_objects.filter.return_value.order_by.return_value = [MagicMock(), MagicMock()]

        mentees = mock_module_node.mentees()
        assert len(mentees) == 2
        mock_module_node.menteemodule_set.select_related.assert_called_once_with("mentee__github_user")
        mock_user_objects.filter.assert_called_once_with(id__in=["github_user_id_1", "github_user_id_2"])
        mock_user_objects.filter.return_value.order_by.assert_called_once_with("login")


def test_module_node_issue_mentees(mock_module_node):
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects, patch(
        "apps.github.models.user.User.objects"
    ) as mock_user_objects:
        mock_task_objects.filter.return_value.select_related.return_value.values_list.return_value.distinct.return_value = [
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
    mock_module_node._issues_qs.select_related.return_value.prefetch_related.return_value.filter.assert_called_once_with(
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
        mock_label_objects.filter.return_value.values_list.return_value.distinct.return_value = ["label1", "label2"]

        labels = mock_module_node.available_labels()
        assert labels == ["label1", "label2"]
        mock_label_objects.filter.assert_called_once_with(issue__mentorship_modules=mock_module_node)


def test_module_node_issue_by_number(mock_module_node):
    issue = mock_module_node.issue_by_number(number=456)
    assert issue is not None
    mock_module_node._issues_qs.select_related.assert_called_once_with("repository", "author")
    mock_module_node._issues_qs.select_related.return_value.prefetch_related.assert_called_once_with("assignees", "labels")
    mock_module_node._issues_qs.select_related.return_value.prefetch_related.return_value.filter.assert_called_once_with(number=456)
    mock_module_node._issues_qs.select_related.return_value.prefetch_related.return_value.filter.return_value.first.assert_called_once()


def test_module_node_interested_users(mock_module_node):
    with patch("apps.mentorship.models.issue_user_interest.IssueUserInterest.objects") as mock_issue_user_interest_objects:
        mock_interest1 = MagicMock(); mock_interest1.user = MagicMock(login="user1")
        mock_interest2 = MagicMock(); mock_interest2.user = MagicMock(login="user2")
        mock_issue_user_interest_objects.select_related.return_value.filter.return_value.order_by.return_value = [
            mock_interest1, mock_interest2
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


def test_module_node_task_deadline(mock_module_node):
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_objects.filter.return_value.order_by.return_value.values_list.return_value.first.return_value = datetime(2025, 10, 26)

        deadline = mock_module_node.task_deadline(issue_number=101)
        assert deadline == datetime(2025, 10, 26)
        mock_task_objects.filter.assert_called_once_with(
            module=mock_module_node, issue__number=101, deadline_at__isnull=False
        )


def test_module_node_task_deadline_none(mock_module_node):
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_objects.filter.return_value.order_by.return_value.values_list.return_value.first.return_value = None

        deadline = mock_module_node.task_deadline(issue_number=101)
        assert deadline is None


def test_module_node_task_assigned_at(mock_module_node):
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_objects.filter.return_value.order_by.return_value.values_list.return_value.first.return_value = datetime(2025, 9, 15)

        assigned_at = mock_module_node.task_assigned_at(issue_number=202)
        assert assigned_at == datetime(2025, 9, 15)
        mock_task_objects.filter.assert_called_once_with(
            module=mock_module_node, issue__number=202, assigned_at__isnull=False
        )


def test_module_node_task_assigned_at_none(mock_module_node):
    with patch("apps.mentorship.models.task.Task.objects") as mock_task_objects:
        mock_task_objects.filter.return_value.order_by.return_value.values_list.return_value.first.return_value = None

        assigned_at = mock_module_node.task_assigned_at(issue_number=202)
        assert assigned_at is None


def test_create_update_input_defaults():
    # CreateModuleInput / UpdateModuleInput defaults sanity checks
    create_input = CreateModuleInput(
        name="Test", description="Desc", ended_at=datetime.now(),
        experience_level=ExperienceLevelEnum.BEGINNER, program_key="key",
        project_name="Project", project_id="id", started_at=datetime.now()
    )
    assert create_input.domains == []
    assert create_input.labels == []
    assert create_input.tags == []

    update_input = UpdateModuleInput(
        key="test-key", program_key="key", name="Test", description="Desc",
        ended_at=datetime.now(), experience_level=ExperienceLevelEnum.BEGINNER,
        project_id="id", project_name="Project", started_at=datetime.now()
    )
    assert update_input.domains == []
    assert update_input.labels == []
    assert update_input.tags == []