from datetime import datetime

import pytest

from apps.api.rest.v0.milestone import MilestoneDetail


class TestMilestoneSchema:
    @pytest.mark.parametrize(
        "milestone_data",
        [
            {
                "body": "This is a test milestone for Q1",
                "closed_issues_count": 5,
                "created_at": "2024-01-01T00:00:00Z",
                "due_on": "2024-03-31T23:59:59Z",
                "number": 1,
                "open_issues_count": 3,
                "state": "open",
                "title": "Q1 2024 Release",
                "updated_at": "2024-01-15T00:00:00Z",
                "url": "https://github.com/OWASP/Nest/milestone/1",
            },
            {
                "body": "Completed milestone for Q4 2023",
                "closed_issues_count": 15,
                "created_at": "2023-10-01T00:00:00Z",
                "due_on": "2023-12-31T23:59:59Z",
                "number": 2,
                "open_issues_count": 0,
                "state": "closed",
                "title": "Q4 2023 Release",
                "updated_at": "2024-01-05T00:00:00Z",
                "url": "https://github.com/OWASP/Nest/milestone/2",
            },
            {
                "body": "Milestone without due date",
                "closed_issues_count": 2,
                "created_at": "2024-02-01T00:00:00Z",
                "due_on": None,
                "number": 3,
                "open_issues_count": 8,
                "state": "open",
                "title": "Backlog",
                "updated_at": "2024-02-15T00:00:00Z",
                "url": "https://github.com/OWASP/Nest/milestone/3",
            },
        ],
    )
    def test_milestone_schema(self, milestone_data):
        milestone = MilestoneDetail(**milestone_data)

        assert milestone.body == milestone_data["body"]
        assert milestone.closed_issues_count == milestone_data["closed_issues_count"]
        assert milestone.created_at == datetime.fromisoformat(milestone_data["created_at"])
        if milestone_data["due_on"]:
            assert milestone.due_on == datetime.fromisoformat(milestone_data["due_on"])
        else:
            assert milestone.due_on is None
        assert milestone.number == milestone_data["number"]
        assert milestone.open_issues_count == milestone_data["open_issues_count"]
        assert milestone.state == milestone_data["state"]
        assert milestone.title == milestone_data["title"]
        assert milestone.updated_at == datetime.fromisoformat(milestone_data["updated_at"])
        assert milestone.url == milestone_data["url"]

    def test_milestone_schema_with_minimal_data(self):
        """Test milestone schema with minimal required fields."""
        minimal_data = {
            "body": "",
            "closed_issues_count": 0,
            "created_at": "2024-01-01T00:00:00Z",
            "due_on": None,
            "number": 1,
            "open_issues_count": 0,
            "state": "open",
            "title": "Test Milestone",
            "updated_at": "2024-01-01T00:00:00Z",
            "url": "https://github.com/test/repo/milestone/1",
        }
        milestone = MilestoneDetail(**minimal_data)

        assert milestone.body == ""
        assert milestone.closed_issues_count == 0
        assert milestone.due_on is None
        assert milestone.number == 1
        assert milestone.open_issues_count == 0
        assert milestone.title == "Test Milestone"
        assert milestone.state == "open"
