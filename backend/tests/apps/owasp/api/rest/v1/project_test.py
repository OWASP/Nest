from datetime import datetime

import pytest

from apps.owasp.api.rest.v1.project import ProjectSchema


@pytest.mark.parametrize(
    "project_data",
    [
        {
            "name": "another project",
            "description": "A test project by owasp",
            "level": "other",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
        },
        {
            "name": "this is a project",
            "description": "this is not a project, this is just a file",
            "level": "incubator",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
        },
    ],
)
def test_project_serializer_validation(project_data):
    project = ProjectSchema(**project_data)
    assert project.name == project_data["name"]
    assert project.description == project_data["description"]
    assert project.level == project_data["level"]
    assert project.created_at == datetime.fromisoformat(project_data["created_at"])
    assert project.updated_at == datetime.fromisoformat(project_data["updated_at"])
