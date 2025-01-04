from apps.github.models.mixins.repository import RepositoryIndexMixin

CONTRIBUTORS_COUNT = 5
FORKS_COUNT = 5
OPEN_ISSUES_COUNT = 5
STARS_COUNT = 5


class TestRepositoryIndexMixin:
    def test_repository_index(self):
        class MockModel(RepositoryIndexMixin):
            def __init__(self):
                self.contributors_count = 5
                self.description = "Description"
                self.forks_count = 5
                self.top_languages = ["Python", "JavaScript"]
                self.name = "Name"
                self.open_issues_count = 5
                self.pushed_at = "2021-01-01"
                self.stars_count = 5
                self.topics = ["Topic1", "Topic2"]

        mock_instance = MockModel()

        assert isinstance(mock_instance, RepositoryIndexMixin)

        assert mock_instance.idx_contributors_count == CONTRIBUTORS_COUNT
        assert mock_instance.idx_description == "Description"
        assert mock_instance.idx_forks_count == FORKS_COUNT
        assert mock_instance.idx_languages == ["Python", "JavaScript"]
        assert mock_instance.idx_name == "Name"
        assert mock_instance.idx_open_issues_count == OPEN_ISSUES_COUNT
        assert mock_instance.idx_pushed_at == "2021-01-01"
        assert mock_instance.idx_stars_count == STARS_COUNT
        assert mock_instance.idx_topics == ["Topic1", "Topic2"]
