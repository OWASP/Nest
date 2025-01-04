from apps.github.models.mixins.issue import IssueIndexMixin


class TestIssueIndexMixin:
    def test_issue_index(self):
        class MockModel(IssueIndexMixin):
            created_at = "2021-09-01T00:00:00Z"
            updated_at = "2021-09-01T00:00:00Z"
            url = "url"
            title = "title"
            summary = "summary"
            hint = "hint"
            comments_count = 5

        mock_instance = MockModel()

        assert mock_instance.idx_created_at == "2021-09-01T00:00:00Z"
        assert mock_instance.idx_updated_at == "2021-09-01T00:00:00Z"
        assert mock_instance.idx_url == "url"
        assert mock_instance.idx_title == "title"
        assert mock_instance.idx_summary == "summary"
        assert mock_instance.idx_hint == "hint"
        assert mock_instance.idx_comments_count == 5
