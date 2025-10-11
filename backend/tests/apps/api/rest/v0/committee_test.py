from datetime import datetime

import pytest

from apps.api.rest.v0.committee import CommitteeDetail


@pytest.mark.parametrize(
    "committee_data",
    [
        {
            "created_at": "2024-11-01T00:00:00Z",
            "description": "A test committee",
            "key": "test-committee",
            "name": "Test Committee",
            "updated_at": "2024-07-02T00:00:00Z",
        },
        {
            "created_at": "2023-12-01T00:00:00Z",
            "description": "A committee without a name",
            "key": "this-is-a-committee",
            "name": "this is a committee",
            "updated_at": "2023-09-02T00:00:00Z",
        },
    ],
)
def test_committee_serializer_validation(committee_data):
    class MockCommittee:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
            self.nest_key = data["key"]

    committee = CommitteeDetail.from_orm(MockCommittee(committee_data))

    assert committee.created_at == datetime.fromisoformat(committee_data["created_at"])
    assert committee.description == committee_data["description"]
    assert committee.key == committee_data["key"]
    assert committee.name == committee_data["name"]
    assert committee.updated_at == datetime.fromisoformat(committee_data["updated_at"])
