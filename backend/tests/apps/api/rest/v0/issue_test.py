from datetime import datetime

import pytest

from apps.api.rest.v0.issue import IssueDetail


class TestIssueSchema:
    @pytest.mark.parametrize(
        "issue_data",
        [
            {
                "body": "This is a test issue 1",
                "created_at": "2024-12-30T00:00:00Z",
                "state": "open",
                "title": "Test Issue 1",
                "updated_at": "2024-12-30T00:00:00Z",
                "url": "https://example.com/issues/1",
            },
            {
                "body": "This is a test issue 2",
                "created_at": "2024-12-29T00:00:00Z",
                "state": "closed",
                "title": "Test Issue 2",
                "updated_at": "2024-12-30T00:00:00Z",
                "url": "https://example.com/issues/2",
            },
        ],
    )
    def test_issue_schema(self, issue_data):
        issue = IssueDetail(**issue_data)

        assert issue.body == issue_data["body"]
        assert issue.created_at == datetime.fromisoformat(issue_data["created_at"])
        assert issue.state == issue_data["state"]
        assert issue.title == issue_data["title"]
        assert issue.updated_at == datetime.fromisoformat(issue_data["updated_at"])
        assert issue.url == issue_data["url"]
