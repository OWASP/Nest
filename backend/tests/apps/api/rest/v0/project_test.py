from datetime import datetime

import pytest

from apps.api.rest.v0.project import ProjectDetail


@pytest.mark.parametrize(
    "project_data",
    [
        {
            "created_at": "2023-01-01T00:00:00Z",
            "description": "A test project by owasp",
            "key": "another-project",
            "level": "other",
            "name": "another project",
            "updated_at": "2023-01-02T00:00:00Z",
        },
        {
            "created_at": "2023-01-01T00:00:00Z",
            "description": "this is not a project, this is just a file",
            "key": "this-is-a-project",
            "level": "incubator",
            "name": "this is a project",
            "updated_at": "2023-01-02T00:00:00Z",
        },
    ],
)
def test_project_serializer_validation(project_data):
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
