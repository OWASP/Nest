from datetime import datetime

import pytest

from apps.api.rest.v0.project import ProjectDetail


@pytest.mark.parametrize(
    "project_data",
    [
        {
            "key": "another-project",
            "name": "another project",
            "description": "A test project by owasp",
            "level": "other",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
        },
        {
            "key": "this-is-a-project",
            "name": "this is a project",
            "description": "this is not a project, this is just a file",
            "level": "incubator",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
        },
    ],
)
def test_project_serializer_validation(project_data):
    # Create a mock object with nest_key property
    class MockProject:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
            self.nest_key = data["key"]

    project = ProjectDetail.from_orm(MockProject(project_data))

    assert project.created_at == datetime.fromisoformat(project_data["created_at"])
    assert project.description == project_data["description"]
    assert project.key == project_data["key"]
    assert project.level == project_data["level"]
    assert project.name == project_data["name"]
    assert project.updated_at == datetime.fromisoformat(project_data["updated_at"])
