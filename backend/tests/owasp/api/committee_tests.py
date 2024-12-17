import pytest

from apps.owasp.api.committee import CommitteeSerializer


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
    serializer = CommitteeSerializer(data=data)
    is_valid = serializer.is_valid()

    # Assert that the result matches the expected outcome
    assert is_valid == expected
