from apps.github.management.commands.github_update_pull_requests import Command


class TestGithubUpdatePullRequests:
    def test_handle_links_issues(self, mocker):
        mock_repo = mocker.Mock(name="Repository", id=1)
        mock_repo.name = "test-repo"

        mock_issue = mocker.Mock(name="Issue", id=10, number=123)
        mock_issue.repository = mock_repo

        mock_pr = mocker.Mock(name="PullRequest", id=100, number=456)
        mock_pr.repository = mock_repo
        mock_pr.body = "This closes #123"
        mock_pr.related_issues = mocker.Mock()
        mock_pr.related_issues.values_list.return_value = []

        mock_pr_qs = mocker.Mock()
        mock_pr_qs.select_related.return_value.all.return_value = [mock_pr]

        mocker.patch(
            "apps.github.management.commands.github_update_pull_requests.PullRequest.objects",
            mock_pr_qs,
        )

        mock_issue_qs = mocker.Mock()
        mock_issue_qs.filter.return_value = [mock_issue]
        mocker.patch(
            "apps.github.management.commands.github_update_pull_requests.Issue.objects",
            mock_issue_qs,
        )

        command = Command()
        command.stdout = mocker.Mock()
        command.handle()

        mock_issue_qs.filter.assert_called_with(repository=mock_repo, number__in={123})
        mock_pr.related_issues.add.assert_called_with(10)

    def test_handle_no_repo_skipped(self, mocker):
        mock_pr = mocker.Mock(name="PullRequest", id=100, number=456)
        mock_pr.repository = None
        mock_pr.related_issues = mocker.Mock()

        mock_pr_qs = mocker.Mock()
        mock_pr_qs.select_related.return_value.all.return_value = [mock_pr]

        mocker.patch(
            "apps.github.management.commands.github_update_pull_requests.PullRequest.objects",
            mock_pr_qs,
        )

        command = Command()
        command.stdout = mocker.Mock()
        command.handle()

        mock_pr.related_issues.add.assert_not_called()

    def test_handle_no_keywords(self, mocker):
        mock_repo = mocker.Mock(name="Repository")
        mock_pr = mocker.Mock(name="PullRequest", id=100, number=456)
        mock_pr.repository = mock_repo
        mock_pr.body = "Just a normal PR"

        mock_pr_qs = mocker.Mock()
        mock_pr_qs.select_related.return_value.all.return_value = [mock_pr]
        mocker.patch(
            "apps.github.management.commands.github_update_pull_requests.PullRequest.objects",
            mock_pr_qs,
        )

        mock_issue_objects = mocker.patch(
            "apps.github.management.commands.github_update_pull_requests.Issue.objects"
        )

        command = Command()
        command.stdout = mocker.Mock()
        command.handle()

        mock_issue_objects.filter.assert_not_called()
