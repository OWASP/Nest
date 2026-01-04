from unittest.mock import MagicMock

from apps.mentorship.models import Task
from apps.github.models import Issue, User as GithubUser


class TestTaskUnit:
    def test_str_when_assigned(self):
        issue = MagicMock(spec=Issue)
        issue.title = "Task Issue Title"

        assignee = MagicMock(spec=GithubUser)
        assignee.login = "taskassignee"

        task = MagicMock(spec=Task)
        task.issue = issue
        task.assignee = assignee

        expected = f"Task: '{issue.title}' assigned to {assignee.login}"
        assert Task.__str__(task) == expected

    def test_str_when_unassigned(self):
        issue = MagicMock(spec=Issue)
        issue.title = "Task Issue Title"

        task = MagicMock(spec=Task)
        task.issue = issue
        task.assignee = None

        expected = f"Task: {issue.title} (Unassigned)"
        assert Task.__str__(task) == expected

    def test_status_constants(self):
        assert Task.Status.TODO == "TODO"
        assert Task.Status.IN_PROGRESS == "IN_PROGRESS"
        assert Task.Status.IN_REVIEW == "IN_REVIEW"
        assert Task.Status.COMPLETED == "COMPLETED"
