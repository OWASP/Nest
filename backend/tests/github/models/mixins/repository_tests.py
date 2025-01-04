from apps.github.models.mixins.repository import RepositoryIndexMixin


class TestRepositoryIndexMixin:
    CONTRIBUTORS_COUNT = 5
    DESCRIPTION = "Description"
    FORKS_COUNT = 5
    TOP_LANGUAGES = ["Python", "JavaScript"]
    NAME = "Name"
    OPEN_ISSUES_COUNT = 5
    PUSHED_AT = "2021-01-01"
    STARS_COUNT = 5
    TOPICS = ["Topic1", "Topic2"]

    def test_repository_index(self):
        class MockModel(RepositoryIndexMixin):
            idx_contributors_count = TestRepositoryIndexMixin.CONTRIBUTORS_COUNT
            idx_description = TestRepositoryIndexMixin.DESCRIPTION
            idx_forks_count = TestRepositoryIndexMixin.FORKS_COUNT
            idx_languages = TestRepositoryIndexMixin.TOP_LANGUAGES
            idx_name = TestRepositoryIndexMixin.NAME
            idx_open_issues_count = TestRepositoryIndexMixin.OPEN_ISSUES_COUNT
            idx_pushed_at = TestRepositoryIndexMixin.PUSHED_AT
            idx_stars_count = TestRepositoryIndexMixin.STARS_COUNT
            idx_topics = TestRepositoryIndexMixin.TOPICS

        mock_instance = MockModel()

        assert mock_instance.idx_contributors_count == TestRepositoryIndexMixin.CONTRIBUTORS_COUNT
        assert mock_instance.idx_description == TestRepositoryIndexMixin.DESCRIPTION
        assert mock_instance.idx_forks_count == TestRepositoryIndexMixin.FORKS_COUNT
        assert mock_instance.idx_languages == TestRepositoryIndexMixin.TOP_LANGUAGES
        assert mock_instance.idx_name == TestRepositoryIndexMixin.NAME
        assert mock_instance.idx_open_issues_count == TestRepositoryIndexMixin.OPEN_ISSUES_COUNT
        assert mock_instance.idx_pushed_at == TestRepositoryIndexMixin.PUSHED_AT
        assert mock_instance.idx_stars_count == TestRepositoryIndexMixin.STARS_COUNT
        assert mock_instance.idx_topics == TestRepositoryIndexMixin.TOPICS
