import pytest

from apps.github.api.repository import RepositorySerializer


class TestRepositorySerializer:
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
    def test_repository_serializer(self, repository_data):
        serializer = RepositorySerializer(data=repository_data)
        assert serializer.is_valid()
        validated_data = serializer.validated_data

        validated_data["created_at"] = (
            validated_data["created_at"].isoformat().replace("+00:00", "Z")
        )
        validated_data["updated_at"] = (
            validated_data["updated_at"].isoformat().replace("+00:00", "Z")
        )
        assert validated_data == repository_data
