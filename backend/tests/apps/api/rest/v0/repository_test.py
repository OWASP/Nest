from datetime import datetime

import pytest

from apps.api.rest.v0.repository import RepositoryDetail


class TestRepositorySchema:
    @pytest.mark.parametrize(
        "repository_data",
        [
            {
                "created_at": "2024-12-30T00:00:00Z",
                "description": "Description for Repo1",
                "name": "Repo1",
                "updated_at": "2024-12-30T00:00:00Z",
            },
            {
                "created_at": "2024-12-29T00:00:00Z",
                "description": "Description for Repo2",
                "name": "Repo2",
                "updated_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    def test_repository_schema(self, repository_data):
        repository = RepositoryDetail(**repository_data)

        assert repository.created_at == datetime.fromisoformat(repository_data["created_at"])
        assert repository.description == repository_data["description"]
        assert repository.name == repository_data["name"]
        assert repository.updated_at == datetime.fromisoformat(repository_data["updated_at"])
