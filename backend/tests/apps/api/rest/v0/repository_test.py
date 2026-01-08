from datetime import datetime

import pytest

from apps.api.rest.v0.repository import RepositoryDetail


class TestRepositorySchema:
    @pytest.mark.parametrize(
        "repository_data",
        [
            {
                "commits_count": 0,
                "contributors_count": 0,
                "created_at": "2024-12-30T00:00:00Z",
                "description": "Description for Repo1",
                "forks_count": 0,
                "name": "Repo1",
                "open_issues_count": 0,
                "stars_count": 0,
                "updated_at": "2024-12-30T00:00:00Z",
            },
            {
                "commits_count": 20,
                "contributors_count": 5,
                "created_at": "2024-12-29T00:00:00Z",
                "description": "Description for Repo2",
                "forks_count": 3,
                "name": "Repo2",
                "open_issues_count": 2,
                "stars_count": 10,
                "updated_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    def test_repository_schema(self, repository_data):
        repository = RepositoryDetail(**repository_data)

        assert repository.commits_count == repository_data["commits_count"]
        assert repository.contributors_count == repository_data["contributors_count"]
        assert repository.created_at == datetime.fromisoformat(repository_data["created_at"])
        assert repository.description == repository_data["description"]
        assert repository.forks_count == repository_data["forks_count"]
        assert repository.name == repository_data["name"]
        assert repository.open_issues_count == repository_data["open_issues_count"]
        assert repository.stars_count == repository_data["stars_count"]
        assert repository.updated_at == datetime.fromisoformat(repository_data["updated_at"])
