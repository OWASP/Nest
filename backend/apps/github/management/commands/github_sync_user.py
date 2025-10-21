"""A command to sync GitHub user commits, pull requests, and issues across OWASP organizations."""

import logging
from datetime import UTC, datetime

from django.core.management.base import BaseCommand
from github.GithubException import GithubException

from apps.github.auth import get_github_client
from apps.github.models.commit import Commit
from apps.github.models.issue import Issue
from apps.github.models.organization import Organization
from apps.github.models.pull_request import PullRequest
from apps.github.models.repository import Repository
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User
from apps.owasp.models.member_profile import MemberProfile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sync commits, PRs, and issues by a user across OWASP orgs."""

    help = "Sync commits, PRs, and issues by a user across OWASP orgs"

    def add_arguments(self, parser):
        """Add command-line arguments.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "username",
            type=str,
            help="GitHub username to fetch commits, PRs, and issues for",
        )
        parser.add_argument(
            "--start-at",
            type=str,
            help="Start date (YYYY-MM-DD). Defaults to January 1st of current year.",
        )
        parser.add_argument(
            "--end-at",
            type=str,
            help="End date (YYYY-MM-DD). Defaults to October 1st of current year.",
        )
        parser.add_argument(
            "--skip-sync",
            action="store_true",
            help="Skip syncing; only populate first_contribution_at if null",
        )

    def parse_date(self, date_str: str | None, default: datetime) -> datetime:
        """Parse date string or return default.

        Args:
            date_str (str | None): Date string in YYYY-MM-DD format.
            default (datetime): Default datetime to use if date_str is None.

        Returns:
            datetime: Parsed datetime or default.

        Raises:
            ValueError: If date string format is invalid.

        """
        if not date_str:
            return default

        try:
            return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
        except ValueError:
            error_msg = f"Invalid date format: {date_str}. Use YYYY-MM-DD."
            self.stderr.write(self.style.ERROR(error_msg))
            raise

    def populate_first_contribution_only(self, username: str, user: User, gh):
        """Populate only the first_contribution_at field using GitHub API.

        Args:
            username (str): GitHub username
            user (User): User model instance
            gh: GitHub client instance

        """
        profile, _created = MemberProfile.objects.get_or_create(github_user=user)

        if profile.first_contribution_at is not None:
            self.stdout.write(
                self.style.WARNING(
                    f"First contribution date already set to "
                    f"{profile.first_contribution_at.strftime('%Y-%m-%d')}. Skipping."
                )
            )
            return

        # Get OWASP organizations
        organizations = Organization.objects.filter(is_owasp_related_organization=True)
        if not organizations.exists():
            self.stderr.write(self.style.ERROR("No OWASP organizations found"))
            return

        org_names = [org.login for org in organizations]
        self.stdout.write(f"Searching across {len(org_names)} OWASP organizations...")

        earliest_dates = []

        # Search for earliest commit across all organizations
        commit_query = f"author:{username} " + " ".join(f"org:{org}" for org in org_names)
        commit_query += " sort:author-date-asc"
        try:
            commits = gh.search_commits(query=commit_query, sort="author-date", order="asc")
            if commits.totalCount > 0:
                first_commit = next(iter(commits))
                earliest_dates.append(
                    (first_commit.commit.author.date, "commit", first_commit.repository.name)
                )
                self.stdout.write(
                    f"  Found earliest commit: {first_commit.commit.author.date} "
                    f"in {first_commit.repository.full_name}"
                )
        except GithubException as e:
            logger.warning("Error searching commits: %s", e)

        # Search for earliest PR
        pr_query = f"author:{username} type:pr " + " ".join(f"org:{org}" for org in org_names)
        pr_query += " sort:created-asc"
        try:
            prs = gh.search_issues(query=pr_query, sort="created", order="asc")
            if prs.totalCount > 0:
                first_pr = next(iter(prs))
                earliest_dates.append((first_pr.created_at, "PR", first_pr.repository.name))
                self.stdout.write(f"  Found earliest PR: {first_pr.created_at}")
        except GithubException as e:
            logger.warning("Error searching PRs: %s", e)

        # Search for earliest issue
        issue_query = f"author:{username} type:issue " + " ".join(
            f"org:{org}" for org in org_names
        )
        issue_query += " sort:created-asc"
        try:
            issues = gh.search_issues(query=issue_query, sort="created", order="asc")
            if issues.totalCount > 0:
                first_issue = next(iter(issues))
                earliest_dates.append(
                    (first_issue.created_at, "issue", first_issue.repository.name)
                )
                self.stdout.write(f"  Found earliest issue: {first_issue.created_at}")
        except GithubException as e:
            logger.warning("Error searching issues: %s", e)

        if earliest_dates:
            # Find the minimum date
            first_contribution_date, contrib_type, repo_name = min(
                earliest_dates, key=lambda x: x[0]
            )
            profile.first_contribution_at = first_contribution_date
            profile.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSet first OWASP contribution: {contrib_type} in {repo_name} "
                    f"on {first_contribution_date.strftime('%Y-%m-%d')}"
                )
            )
            logger.info(
                "Set first OWASP contribution for %s: %s (%s in %s)",
                username,
                first_contribution_date,
                contrib_type,
                repo_name,
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"No contributions found for {username} in OWASP organizations")
            )

    def handle(self, *args, **options):
        """Handle command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        username = options["username"]
        skip_sync = options.get("skip_sync", False)

        gh = get_github_client()

        try:
            gh_user = gh.get_user(username)
            user = User.update_data(gh_user, save=True)
        except GithubException as e:
            self.stderr.write(self.style.ERROR(f"Could not fetch user {username}: {e}"))
            return

        # If skipping sync, populate first contribution if needed and exit
        if skip_sync:
            self.stdout.write("Skipping data sync...")
            self.populate_first_contribution_only(username, user, gh)
            return

        # Default to current year: Jan 1 to Oct 1
        current_year = datetime.now(UTC).year
        default_start = datetime(current_year, 1, 1, tzinfo=UTC)
        default_end = datetime(current_year, 10, 1, tzinfo=UTC)

        end_at = self.parse_date(options.get("end_at"), default_end)
        start_at = self.parse_date(options.get("start_at"), default_start)

        contributed_repos = RepositoryContributor.objects.filter(user=user).select_related(
            "repository__organization"
        )

        if not contributed_repos.exists():
            self.stderr.write(self.style.WARNING(f"No contributions found for {username}"))
            return

        organizations = Organization.objects.filter(
            id__in=contributed_repos.values_list("repository__organization_id", flat=True),
            is_owasp_related_organization=True,
        ).distinct()

        if not organizations.exists():
            self.stderr.write(
                self.style.WARNING(
                    f"{username} has no contributions to OWASP-related organizations"
                )
            )
            return

        org_count = organizations.count()
        self.stdout.write(
            f"Found {org_count} OWASP organization(s) with contributions from {username}"
        )

        repositories_cache = {}
        for repo in Repository.objects.filter(organization__in=organizations).select_related(
            "owner"
        ):
            cache_key = f"{repo.owner.login}/{repo.name}".lower()
            repositories_cache[cache_key] = repo

        logger.info("Cached %s repositories", len(repositories_cache))

        commits_data = []
        committers_data = []
        pull_requests_data = []
        issues_data = []
        date_range = f"{start_at.strftime('%Y-%m-%d')}..{end_at.strftime('%Y-%m-%d')}"
        total_orgs = organizations.count()

        processed_orgs = 0
        for org in organizations:
            processed_orgs += 1
            progress = f"[{processed_orgs}/{total_orgs}]"
            self.stdout.write(f"{progress} Processing organization: {org.login}")
            logger.info(
                "Processing organization %s (%s/%s)",
                org.login,
                processed_orgs,
                total_orgs,
            )

            # Fetch commits
            commit_query = f"author:{username} org:{org.login} committer-date:{date_range}"
            try:
                gh_commits = gh.search_commits(query=commit_query)

                self.stdout.write(f"  Found {gh_commits.totalCount} commits")
                logger.info("Found %s commits in %s", gh_commits.totalCount, org.login)

                processed_commits = 0
                for gh_commit in gh_commits:
                    processed_commits += 1
                    repo_full_name = gh_commit.repository.full_name
                    cache_key = repo_full_name.lower()

                    repo = repositories_cache.get(cache_key)
                    if not repo:
                        logger.warning(
                            "Repository %s not in database, skipping commit", repo_full_name
                        )
                        continue

                    commit_committer = None
                    if gh_commit.committer:
                        commit_committer = User.update_data(gh_commit.committer, save=False)
                        committers_data.append(commit_committer)

                    commit = Commit.update_data(
                        gh_commit,
                        repository=repo,
                        author=user,
                        committer=commit_committer,
                        save=False,
                    )

                    commits_data.append(commit)
                    logger.info(
                        "Processed commit %s/%s: %s in %s",
                        processed_commits,
                        gh_commits.totalCount,
                        gh_commit.sha[:7],
                        repo.name,
                    )

            except GithubException as e:
                error_msg = f"  Error searching commits in {org.login}: {e}"
                self.stderr.write(self.style.WARNING(error_msg))

            # Fetch pull requests
            pr_query = f"author:{username} org:{org.login} type:pr created:{date_range}"
            try:
                gh_prs = gh.search_issues(query=pr_query)

                self.stdout.write(f"  Found {gh_prs.totalCount} pull requests")
                logger.info("Found %s pull requests in %s", gh_prs.totalCount, org.login)

                processed_prs = 0
                for gh_issue in gh_prs:
                    processed_prs += 1
                    repo_full_name = gh_issue.repository.full_name
                    cache_key = repo_full_name.lower()

                    repo = repositories_cache.get(cache_key)
                    if not repo:
                        logger.warning(
                            "Repository %s not in database, skipping PR", repo_full_name
                        )
                        continue

                    # Get the full PR object from the repository
                    # Note: search_issues returns Issue objects which lack PR-specific fields
                    # like merged_at, so we need to fetch the complete PR object
                    try:
                        gh_repo = gh.get_repo(repo_full_name)
                        gh_pr = gh_repo.get_pull(gh_issue.number)
                    except GithubException as e:
                        logger.warning(
                            "Could not fetch PR #%s from %s: %s",
                            gh_issue.number,
                            repo_full_name,
                            e,
                        )
                        continue

                    pull_request = PullRequest.update_data(
                        gh_pr,
                        author=user,
                        repository=repo,
                        save=False,
                    )

                    pull_requests_data.append(pull_request)
                    logger.info(
                        "Processed PR %s/%s: #%s in %s",
                        processed_prs,
                        gh_prs.totalCount,
                        gh_pr.number,
                        repo.name,
                    )

            except GithubException as e:
                error_msg = f"  Error searching PRs in {org.login}: {e}"
                self.stderr.write(self.style.WARNING(error_msg))

            # Fetch issues
            issue_query = f"author:{username} org:{org.login} type:issue created:{date_range}"
            try:
                gh_issues = gh.search_issues(query=issue_query)

                self.stdout.write(f"  Found {gh_issues.totalCount} issues")
                logger.info("Found %s issues in %s", gh_issues.totalCount, org.login)

                processed_issues = 0
                for gh_issue in gh_issues:
                    processed_issues += 1
                    repo_full_name = gh_issue.repository.full_name
                    cache_key = repo_full_name.lower()

                    repo = repositories_cache.get(cache_key)
                    if not repo:
                        logger.warning(
                            "Repository %s not in database, skipping issue", repo_full_name
                        )
                        continue

                    issue = Issue.update_data(
                        gh_issue,
                        author=user,
                        repository=repo,
                        save=False,
                    )

                    issues_data.append(issue)
                    logger.info(
                        "Processed issue %s/%s: #%s in %s",
                        processed_issues,
                        gh_issues.totalCount,
                        gh_issue.number,
                        repo.name,
                    )

            except GithubException as e:
                error_msg = f"  Error searching issues in {org.login}: {e}"
                self.stderr.write(self.style.WARNING(error_msg))

        total_synced = 0

        if committers_data:
            # Deduplicate committers by node_id
            unique_committers = {}
            for committer in committers_data:
                if committer.node_id not in unique_committers:
                    unique_committers[committer.node_id] = committer

            committers_list = list(unique_committers.values())
            logger.info("Bulk saving %s unique committers", len(committers_list))
            User.bulk_save(committers_list)
            self.stdout.write(f"\nSaved {len(committers_list)} unique committer(s)")

            # Reload saved committers and update commit references
            saved_committers = {
                c.node_id: c
                for c in User.objects.filter(node_id__in=[c.node_id for c in committers_list])
            }
            for commit in commits_data:
                if commit.committer and commit.committer.node_id in saved_committers:
                    commit.committer = saved_committers[commit.committer.node_id]

        if commits_data:
            logger.info("Bulk saving %s commits", len(commits_data))
            Commit.bulk_save(commits_data)
            total_synced += len(commits_data)
            self.stdout.write(f"Saved {len(commits_data)} commit(s)")
            logger.info("Successfully synced %s commits for %s", len(commits_data), username)

        if pull_requests_data:
            logger.info("Bulk saving %s pull requests", len(pull_requests_data))
            PullRequest.bulk_save(pull_requests_data)
            total_synced += len(pull_requests_data)
            self.stdout.write(f"Saved {len(pull_requests_data)} pull request(s)")
            logger.info(
                "Successfully synced %s pull requests for %s",
                len(pull_requests_data),
                username,
            )

        if issues_data:
            logger.info("Bulk saving %s issues", len(issues_data))
            Issue.bulk_save(issues_data)
            total_synced += len(issues_data)
            self.stdout.write(f"Saved {len(issues_data)} issue(s)")
            logger.info(
                "Successfully synced %s issues for %s",
                len(issues_data),
                username,
            )

        if total_synced:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nTotal: Synced {len(pull_requests_data)} PRs, "
                    f"{len(issues_data)} issues, and "
                    f"{len(commits_data)} commits for {username}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"No PRs, issues, or commits found for {username}")
            )
            logger.warning("No PRs, issues, or commits found for %s", username)

        # Always populate first contribution date if not already set
        self.populate_first_contribution_only(username, user, gh)
