from apps.github.models.mixins.issue import IssueIndexMixin


class TestIssueIndexMixin:
    def test_idx_created_at(self):
        class MockModel(IssueIndexMixin):
            created_at = "2021-09-01T00:00:00Z"

        mock_instance = MockModel()
        assert mock_instance.idx_created_at == "2021-09-01T00:00:00Z"

    def test_idx_url(self):
        class MockModel(IssueIndexMixin):
            url = "url"

        mock_instance = MockModel()
        assert mock_instance.idx_url == "url"

    def test_updated_at(self):
        class MockModel(IssueIndexMixin):
            updated_at = "2021-09-01T00:00:00Z"

        mock_instance = MockModel()
        assert mock_instance.idx_updated_at == "2021-09-01T00:00:00Z"

    def test_idx_title(self):
        class MockModel(IssueIndexMixin):
            title = "title"

        mock_instance = MockModel()
        assert mock_instance.idx_title == "title"

    def test_idx_summary(self):
        class MockModel(IssueIndexMixin):
            summary = "summary"

        mock_instance = MockModel()
        assert mock_instance.idx_summary == "summary"

    def test_idx_hint(self):
        class MockModel(IssueIndexMixin):
            hint = "hint"

        mock_instance = MockModel()
        assert mock_instance.idx_hint == "hint"

    def test_idx_comments_count(self):
        default_comment_count = 5

        class MockModel(IssueIndexMixin):
            comments_count = default_comment_count

        mock_instance = MockModel()
        assert mock_instance.idx_comments_count == default_comment_count
