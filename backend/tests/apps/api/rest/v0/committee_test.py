from datetime import datetime

import pytest

from apps.api.rest.v0.committee import CommitteeSchema


@pytest.mark.parametrize(
    "committee_data",
    [
        {
            "name": "Test Committee",
            "description": "A test committee",
            "created_at": "2024-11-01T00:00:00Z",
            "updated_at": "2024-07-02T00:00:00Z",
        },
        {
            "name": "this is a committee",
            "description": "A committee without a name",
            "created_at": "2023-12-01T00:00:00Z",
            "updated_at": "2023-09-02T00:00:00Z",
        },
    ],
)
def test_committee_serializer_validation(committee_data):
    committee = CommitteeSchema(**committee_data)

    assert committee.name == committee_data["name"]
    assert committee.description == committee_data["description"]
    assert committee.created_at == datetime.fromisoformat(committee_data["created_at"])
    assert committee.updated_at == datetime.fromisoformat(committee_data["updated_at"])
