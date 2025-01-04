from apps.github.models.mixins.repository import RepositoryIndexMixin


class TestRepositoryIndexMixin:
    def test_repository_index(self):
        class MockModel(RepositoryIndexMixin):
            contributors_count = 5
            description = "Description"
            forks_count = 5
            top_languages = ["Python", "JavaScript"]
            name = "Name"
            open_issues_count = 5
            pushed_at = "2021-01-01"
            stars_count = 5
            topics = ["Topic1", "Topic2"]

        mock_instance = MockModel()

        assert mock_instance.idx_contributors_count == 5
        assert mock_instance.idx_description == "Description"
        assert mock_instance.idx_forks_count == 5
        assert mock_instance.idx_languages == ["Python", "JavaScript"]
        assert mock_instance.idx_name == "Name"
        assert mock_instance.idx_open_issues_count == 5
        assert mock_instance.idx_pushed_at == "2021-01-01"
        assert mock_instance.idx_stars_count == 5
        assert mock_instance.idx_topics == ["Topic1", "Topic2"]
