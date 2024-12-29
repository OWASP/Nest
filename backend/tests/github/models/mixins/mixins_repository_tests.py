from apps.github.models.mixins.repository import RepositoryIndexMixin


class TestRepositoryMixin:
    def test_idx_contributors_count(self):
        default_contribution_value = 5

        class MockModel(RepositoryIndexMixin):
            contributors_count = default_contribution_value

        mock_instance = MockModel()
        assert mock_instance.idx_contributors_count == default_contribution_value

    def test_idx_description(self):
        class MockModel(RepositoryIndexMixin):
            description = "Description"

        mock_instance = MockModel()
        assert mock_instance.idx_description == "Description"

    def test_idx_forks_count(self):
        default_value = 5

        class MockModel(RepositoryIndexMixin):
            forks_count = default_value

        mock_instance = MockModel()
        assert mock_instance.idx_forks_count == default_value

    def test_idx_languages(self):
        class MockModel(RepositoryIndexMixin):
            top_languages = ["Python", "JavaScript"]

        mock_instance = MockModel()
        assert mock_instance.idx_languages == ["Python", "JavaScript"]

    def test_idx_name(self):
        class MockModel(RepositoryIndexMixin):
            name = "Name"

        mock_instance = MockModel()
        assert mock_instance.idx_name == "Name"

    def test_idx_open_issues_count(self):
        default_value = 5

        class MockModel(RepositoryIndexMixin):
            open_issues_count = default_value

        mock_instance = MockModel()
        assert mock_instance.idx_open_issues_count == default_value

    def test_idx_pushed_at(self):
        class MockModel(RepositoryIndexMixin):
            pushed_at = "2021-01-01"

        mock_instance = MockModel()
        assert mock_instance.idx_pushed_at == "2021-01-01"

    def test_idx_stars_count(self):
        default_value = 5

        class MockModel(RepositoryIndexMixin):
            stars_count = default_value

        mock_instance = MockModel()
        assert mock_instance.idx_stars_count == default_value

    def test_idx_topics(self):
        class MockModel(RepositoryIndexMixin):
            topics = ["Topic1", "Topic2"]

        mock_instance = MockModel()
        assert mock_instance.idx_topics == ["Topic1", "Topic2"]
