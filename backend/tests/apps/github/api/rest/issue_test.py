from datetime import datetime

import pytest

from apps.github.api.rest.v1.issue import IssueSchema


class TestIssueSchema:
    @pytest.mark.parametrize(
        "issue_data",
        [
            {
                "title": "Test Issue 1",
                "body": "This is a test issue 1",
                "state": "open",
                "url": "https://example.com/issues/1",
                "created_at": "2024-12-30T00:00:00Z",
                "updated_at": "2024-12-30T00:00:00Z",
            },
            {
                "title": "Test Issue 2",
                "body": "This is a test issue 2",
                "state": "closed",
                "url": "https://example.com/issues/2",
                "created_at": "2024-12-29T00:00:00Z",
                "updated_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    def test_issue_schema(self, issue_data):
        schema = IssueSchema(**issue_data)

        assert schema.title == issue_data["title"]
        assert schema.body == issue_data["body"]
        assert schema.state == issue_data["state"]
        assert schema.url == issue_data["url"]

        assert schema.created_at == datetime.fromisoformat(issue_data["created_at"])
        assert schema.updated_at == datetime.fromisoformat(issue_data["updated_at"])
