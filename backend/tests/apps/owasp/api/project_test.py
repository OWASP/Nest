import pytest

from apps.owasp.api.project import ProjectSerializer


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            {
                "name": "another project",
                "description": "A test project by owasp",
                "level": "other",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
            },
            True,
        ),
        (
            {
                "name": "this is a project",
                "description": "this is not a project, this is just a file",
                "level": "Hello",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
            },
            False,
        ),
    ],
)
def test_project_serializer_validation(data, expected):
    serializer = ProjectSerializer(data=data)
    is_valid = serializer.is_valid()

    assert is_valid == expected
