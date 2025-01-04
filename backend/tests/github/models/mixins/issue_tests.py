from apps.github.models.mixins.issue import IssueIndexMixin


class TestIssueIndexMixin:
    CREATED_AT = "2021-09-01T00:00:00Z"
    UPDATED_AT = "2021-09-01T00:00:00Z"
    URL = "url"
    TITLE = "title"
    SUMMARY = "summary"
    HINT = "hint"
    COMMENTS_COUNT = 5

    def test_issue_index(self):
        class MockModel(IssueIndexMixin):
            idx_created_at = TestIssueIndexMixin.CREATED_AT
            idx_updated_at = TestIssueIndexMixin.UPDATED_AT
            idx_url = TestIssueIndexMixin.URL
            idx_title = TestIssueIndexMixin.TITLE
            idx_summary = TestIssueIndexMixin.SUMMARY
            idx_hint = TestIssueIndexMixin.HINT
            idx_comments_count = TestIssueIndexMixin.COMMENTS_COUNT

        mock_instance = MockModel()

        assert mock_instance.idx_created_at == TestIssueIndexMixin.CREATED_AT
        assert mock_instance.idx_updated_at == TestIssueIndexMixin.UPDATED_AT
        assert mock_instance.idx_url == TestIssueIndexMixin.URL
        assert mock_instance.idx_title == TestIssueIndexMixin.TITLE
        assert mock_instance.idx_summary == TestIssueIndexMixin.SUMMARY
        assert mock_instance.idx_hint == TestIssueIndexMixin.HINT
        assert mock_instance.idx_comments_count == TestIssueIndexMixin.COMMENTS_COUNT
