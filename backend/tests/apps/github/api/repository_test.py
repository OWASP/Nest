from datetime import datetime

import pytest

from apps.github.api.repository import RepositorySchema


class TestRepositorySchema:
    @pytest.mark.parametrize(
        "repository_data",
        [
            {
                "name": "Repo1",
                "description": "Description for Repo1",
                "created_at": "2024-12-30T00:00:00Z",
                "updated_at": "2024-12-30T00:00:00Z",
            },
            {
                "name": "Repo2",
                "description": "Description for Repo2",
                "created_at": "2024-12-29T00:00:00Z",
                "updated_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    def test_repository_schema(self, repository_data):
        repository = RepositorySchema(**repository_data)

        assert repository.name == repository_data["name"]
        assert repository.description == repository_data["description"]
        assert repository.created_at == datetime.fromisoformat(repository_data["created_at"])
        assert repository.updated_at == datetime.fromisoformat(repository_data["updated_at"])
