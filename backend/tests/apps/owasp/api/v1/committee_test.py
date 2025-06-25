from datetime import datetime

import pytest

from apps.owasp.api.v1.committee import CommitteeSchema


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            {
                "name": "Test Project",
                "description": "A test project",
                "created_at": "2024-11-01T00:00:00Z",
                "updated_at": "2024-07-02T00:00:00Z",
            },
            True,
        ),
        (
            {
                "name": "this is a project",
                "description": "A project without a name",
                "created_at": "2023-12-01T00:00:00Z",
                "updated_at": "2023-09-02T00:00:00Z",
            },
            True,
        ),
    ],
)
def test_committee_serializer_validation(data, expected):
    committee = CommitteeSchema(**data)
    assert committee.name == data["name"]
    assert committee.description == data["description"]
    assert committee.created_at == datetime.fromisoformat(data["created_at"])
    assert committee.updated_at == datetime.fromisoformat(data["updated_at"])
